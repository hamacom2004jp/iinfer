from cmdbox.app import common
from iinfer import version
from pathlib import Path
import getpass
import logging
import platform
import shutil
import sys
import yaml


class Install(object):
    def __init__(self, logger: logging.Logger, wsl_name: str = None, wsl_user: str = None):
        self.logger = logger
        common.set_debug(self.logger, True)
        self.wsl_name = wsl_name
        self.wsl_user = wsl_user

    def redis(self):
        cmd = f"docker pull ubuntu/redis:latest"
        if platform.system() == 'Windows':
            if self.wsl_name is None:
                return {"warn":f"wsl_name option is required."}
            if self.wsl_user is None:
                return {"warn":f"wsl_user option is required."}
            returncode, _, _cmd = common.cmd(f"wsl -d {self.wsl_name} -u {self.wsl_user} {cmd}", self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install redis-server. cmd:{_cmd}")
                return {"error": f"Failed to install redis-server. cmd:{_cmd}"}
            return {"success": f"Success to install redis-server. cmd:{_cmd}"}

        elif platform.system() == 'Linux':
            returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install redis-server. cmd:{_cmd}")
                return {"error": f"Failed to install redis-server. cmd:{_cmd}"}
            return {"success": f"Success to install redis-server. cmd:{_cmd}"}

        else:
            return {"warn":f"Unsupported platform."}

    def server(self, data:Path, install_cmdbox_tgt:str='cmdbox', install_iinfer_tgt:str='iinfer', install_onnx:bool=True,
               install_mmdet:bool=True, install_mmseg:bool=True, install_mmcls:bool=False, install_mmpretrain:bool=True,
               install_insightface=False, install_from:str=None, install_no_python:bool=False, install_compile_python:bool=False,
               install_tag:str=None, install_use_gpu:bool=False):
        """
        iinferが含まれるdockerイメージをインストールします。

        Args:
            data (Path): iinfer-serverのデータディレクトリ
            install_cmdbox_tgt (str): cmdboxのインストール元
            install_iinfer_tgt (str): iinferのインストール元
            install_onnx (bool): onnxをインストールするかどうか
            install_mmdet (bool): mmdetをインストールするかどうか
            install_mmseg (bool): mmsegをインストールするかどうか
            install_mmcls (bool): mmclsをインストールするかどうか
            install_mmpretrain (bool): mmpretrainをインストールするかどうか
            install_insightface (bool): insightfaceをインストールするかどうか
            install_from (str): インストール元dockerイメージ
            install_no_python (bool): pythonをインストールしない
            install_compile_python (bool): pythonをコンパイルしてインストール
            install_tag (str): インストールタグ
            install_use_gpu (bool): GPUを使用するモジュール構成でインストールします。

        Returns:
            dict: 処理結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"Build server command is Unsupported in windows platform."}
        from importlib.resources import read_text
        user = getpass.getuser()
        install_tag = f"_{install_tag}" if install_tag is not None else ''
        with open('Dockerfile', 'w', encoding='utf-8') as fp:
            text = read_text(f'iinfer.docker', 'Dockerfile')
            # cmdboxのインストール設定
            wheel_cmdbox = Path(install_cmdbox_tgt)
            if wheel_cmdbox.exists() and wheel_cmdbox.suffix == '.whl':
                shutil.copy(wheel_cmdbox, Path('.').resolve() / wheel_cmdbox.name)
                install_cmdbox_tgt = f'/home/{user}/{wheel_cmdbox.name}'
                text = text.replace('#{COPY_CMDBOX}', f'COPY {wheel_cmdbox.name} {install_cmdbox_tgt}')
            else:
                text = text.replace('#{COPY_CMDBOX}', '')
            # iinferのインストール設定
            wheel_iinfer = Path(install_iinfer_tgt)
            if wheel_iinfer.exists() and wheel_iinfer.suffix == '.whl':
                shutil.copy(wheel_iinfer, Path('.').resolve() / wheel_iinfer.name)
                install_iinfer_tgt = f'/home/{user}/{wheel_iinfer.name}'
                text = text.replace('#{COPY_IINFER}', f'COPY {wheel_iinfer.name} {install_iinfer_tgt}')
            else:
                text = text.replace('#{COPY_IINFER}', '')

            start_sh_src = Path(__file__).parent.parent / 'docker' / 'scripts'
            start_sh_tgt = f'scripts'
            shutil.copytree(start_sh_src, start_sh_tgt, dirs_exist_ok=True)
            text = text.replace('#{COPY_IINFER_START}', f'COPY {start_sh_tgt} {start_sh_tgt}')

            install_use_gpu_opt = '--install_use_gpu' if install_use_gpu else ''
            base_image = 'python:3.11.9-slim' #'python:3.8.18-slim'
            if install_use_gpu:
                base_image = 'nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04'
            if install_from is not None and install_from != '':
                base_image = install_from
            text = text.replace('#{FROM}', f'FROM {base_image}')
            text = text.replace('${MKUSER}', user)
            #text = text.replace('#{INSTALL_PYTHON}', f'RUN apt-get update && apt-get install -y python3.8 python3.8-distutils python3-pip python-is-python3' if install_use_gpu else '')
            if install_compile_python:
                install_python = f'RUN apt-get update && apt-get install -y build-essential libbz2-dev libdb-dev libreadline-dev libffi-dev libgdbm-dev liblzma-dev ' + \
                                 f'libncursesw5-dev libsqlite3-dev libssl-dev zlib1g-dev uuid-dev tk-dev wget\n' + \
                                 f'RUN wget https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tar.xz\n' + \
                                 f'RUN tar xJf Python-3.11.11.tar.xz && cd Python-3.11.11 && ./configure && make && make install\n' + \
                                 f'RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1'
                text = text.replace('#{INSTALL_PYTHON}', install_python)
            elif not install_no_python:
                text = text.replace('#{INSTALL_PYTHON}', f'RUN apt-get update && apt-get install -y python3.11 python3.11-distutils python3-pip python-is-python3')
            else:
                text = text.replace('#{INSTALL_PYTHON}', '')
            text = text.replace('#{INSTALL_TAG}', install_tag)
            text = text.replace('#{INSTALL_CMDBOX}', install_cmdbox_tgt)
            text = text.replace('#{INSTALL_IINFER}', install_iinfer_tgt)
            text = text.replace('#{INSTALL_ONNX}', f'RUN iinfer -m install -c onnx --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_onnx else '')
            text = text.replace('#{INSTALL_MMDET}', f'RUN iinfer -m install -c mmdet --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_mmdet else '')
            text = text.replace('#{INSTALL_MMSEG}', f'RUN iinfer -m install -c mmseg --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_mmseg else '')
            text = text.replace('#{INSTALL_MMCLS}', f'RUN iinfer -m install -c mmcls --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_mmcls else '')
            text = text.replace('#{INSTALL_MMPRETRAIN}', f'RUN iinfer -m install -c mmpretrain --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_mmpretrain else '')
            text = text.replace('#{INSTALL_INSIGHTFACE}', f'RUN iinfer -m install -c insightface --data /home/{user}/.iinfer {install_use_gpu_opt}' if install_insightface else '')
            fp.write(text)
        docker_compose_path = Path('docker-compose.yml')
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                text = read_text(f'iinfer.docker', 'docker-compose.yml')
                fp.write(text)
        with open(f'docker-compose.yml', 'r+', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)
            services = comp['services']
            common.mkdirs(data)
            services[f'iinfer_server{install_tag}'] = dict(
                image=f'hamacom/iinfer:{version.__version__}{install_tag}',
                container_name=f'iinfer_server{install_tag}',
                environment=dict(
                    TZ='Asia/Tokyo',
                    IINFER_DEBUG='false',
                    REDIS_HOST='${REDIS_HOST:-redis}',
                    REDIS_PORT='${REDIS_PORT:-6379}',
                    REDIS_PASSWORD='${REDIS_PASSWORD:-password}',
                    SVNAME='${SVNAME:-server'+install_tag+'}',
                    LISTEN_PORT='${LISTEN_PORT:-8081}',
                    SVCOUNT='${SVCOUNT:-2}',
                ),
                user=user,
                ports=['${LISTEN_PORT:-8081}:${LISTEN_PORT:-8081}'],
                privileged=True,
                restart='always',
                working_dir=f'/home/{user}',
                devices=['/dev/bus/usb:/dev/bus/usb'],
                volumes=[
                    f'{data}:/home/{user}/.iinfer',
                    f'/home/{user}/scripts:/home/{user}/scripts',
                    f'/home/{user}:/home/{user}'
                ]
            )
            if install_use_gpu:
                services[f'iinfer_server{install_tag}']['deploy'] = dict(
                    resources=dict(reservations=dict(devices=[dict(
                        driver='nvidia',
                        count=1,
                        capabilities=['gpu']
                    )]))
                )
            fp.seek(0)
            yaml.dump(comp, fp)
        cmd = f'docker build -t hamacom/iinfer:{version.__version__}{install_tag} -f Dockerfile .'

        if platform.system() == 'Linux':
            returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
            #os.remove('Dockerfile')
            if returncode != 0:
                self.logger.warning(f"Failed to install iinfer-server. cmd:{_cmd}")
                return {"error": f"Failed to install iinfer-server. cmd:{_cmd}"}
            return {"success": f"Success to install iinfer-server. and docker-compose.yml is copied. cmd:{_cmd}"}

        else:
            return {"warn":f"Unsupported platform."}

    def onnx(self, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd('pip install onnxruntime', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install onnxruntime. cmd:{_cmd}")
            return {"error": f"Failed to install onnxruntime. cmd:{_cmd}"}
        if install_use_gpu:
            returncode, _, _cmd = common.cmd('pip install onnxruntime-gpu', logger=self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install onnxruntime-gpu. cmd:{_cmd}")
                return {"error": f"Failed to install onnxruntime-gpu. cmd:{_cmd}"}
        return {"success": f"Success to install onnxruntime."}

    def insightface(self, data_dir: Path, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd('pip install cython', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install cython. cmd:{_cmd}")
            return {"error": f"Failed to install cython. cmd:{_cmd}"}
        ret = self.onnx(install_use_gpu)
        if "error" in ret: return ret
        returncode, _, _cmd = common.cmd('python -m pip install --upgrade pip setuptools', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install setuptools. cmd:{_cmd}")
            return {"error": f"Failed to install setuptools. cmd:{_cmd}"}
        returncode, _, _cmd = common.cmd('pip install insightface', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install insightface. cmd:{_cmd}")
            return {"error": f"Failed to install insightface. cmd:{_cmd}"}
        return {"success": f"Success to install insightface."}

    def _torch(self, install_use_gpu:bool=False):
        if install_use_gpu:
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
                returncode, _, _cmd = common.cmd('pip install numpy==1.26.3 torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118', logger=self.logger, slise=-1)
            else:
                returncode, _, _cmd = common.cmd('pip install numpy==1.24.1 torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118', logger=self.logger, slise=-1)
        else:
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 10:
                returncode, _, _cmd = common.cmd('pip install numpy==1.26.3 torch==2.1.0 torchvision torchaudio', logger=self.logger, slise=-1)
            else:
                returncode, _, _cmd = common.cmd('pip install numpy==1.24.1 torch==2.1.0 torchvision torchaudio', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install torch torchvision torchaudio. cmd:{_cmd}")
            return {"error": f"Failed to install torch torchvision torchaudio. cmd:{_cmd}"}
        return {"success": f"Success to install torch torchvision torchaudio. cmd:{_cmd}"}

    def _openmin(self, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd('pip install openmim', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install openmim. cmd:{_cmd}")
            return {"error": f"Failed to install openmim. cmd:{_cmd}"}
        return {"success": f"Success to install openmim. cmd:{_cmd}"}

    def _mmcv(self, install_use_gpu:bool=False):
        if install_use_gpu:
            returncode, _, _cmd = common.cmd('pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.1/index.html', logger=self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install mmcv. cmd:{_cmd}")
                return {"error": f"Failed to install mmcv. cmd:{_cmd}"}
        else:
            returncode, _, _cmd = common.cmd('mim install mmcv>=2.0.0', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install mmcv. cmd:{_cmd}")
            return {"error": f"Failed to install mmcv. cmd:{_cmd}"}
        return {"success": f"Success to install mmcv. cmd:{_cmd}"}

    def _transformers(self, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd('pip install accelerate transformers bitsandbytes sentence-transformers', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install accelerate transformers bitsandbytes sentence-transformers. cmd:{_cmd}")
            return {"error": f"Failed to install accelerate transformers bitsandbytes sentence-transformers. cmd:{_cmd}"}
        return {"success": f"Success to install accelerate transformers bitsandbytes sentence-transformers. cmd:{_cmd}"}

    def mmdet(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd(f'git clone https://github.com/open-mmlab/mmdetection.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmdetection. Delete mmdetection as it probably already exists. cmd:{_cmd}")
            return {"error": f"Failed to git clone mmdetection. Delete mmdetection as it probably already exists. cmd:{_cmd}"}
        srcdir = Path('.') / 'mmdetection'
        shutil.copytree(srcdir, data_dir / 'mmdetection', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _, _cmd = common.cmd('mim install mmengine mmdet', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmdet. cmd:{_cmd}")
            return {"error": f"Failed to install mmengine mmdet. cmd:{_cmd}"}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmdetection'}' manually. cmd:{_cmd}"}
        return {"success": f"Success to install mmdet. cmd:{_cmd}"}

    def mmseg(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd(f'git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists. cmd:{_cmd}")
            return {"error": f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists. cmd:{_cmd}"}
        srcdir = Path('.') / 'mmsegmentation'
        shutil.copytree(srcdir, data_dir / 'mmsegmentation', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _, _cmd = common.cmd('mim install mmengine mmsegmentation', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmsegmentation. cmd:{_cmd}")
            return {"error": f"Failed to install mmengine mmsegmentation. cmd:{_cmd}"}

        ret, _, _cmd = common.cmd('pip install ftfy', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install ftfy. cmd:{_cmd}")
            return {"error": f"Failed to install ftfy. cmd:{_cmd}"}

        ret, _, _cmd = common.cmd('pip install regex', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install regex. cmd:{_cmd}")
            return {"error": f"Failed to install regex. cmd:{_cmd}"}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmsegmentation'}' manually."}
        return {"success": f"Success to install mmsegmentation."}

    def mmcls(self, data_dir:Path, install_use_gpu:bool=False):

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _, _cmd = common.cmd('mim install mmengine mmcls', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmcls. cmd:{_cmd}")
            return {"error": f"Failed to install mmengine mmcls. cmd:{_cmd}"}

        return {"success": f"Success to install mmcls. cmd:{_cmd}"}

    def mmpretrain(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd(f'git clone https://github.com/open-mmlab/mmpretrain.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmpretrain. Delete mmpretrain as it probably already exists. cmd:{_cmd}")
            return {"error": f"Failed to git clone mmpretrain. Delete mmpretrain as it probably already exists. cmd:{_cmd}"}
        srcdir = Path('.') / 'mmpretrain'
        shutil.copytree(srcdir, data_dir / 'mmpretrain', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _, _cmd = common.cmd('mim install mmengine mmpretrain', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmpretrain. cmd:{_cmd}")
            return {"error": f"Failed to install mmpretrain. cmd:{_cmd}"}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir}' manually. cmd:{_cmd}"}
        return {"success": f"Success to install mmpretrain. cmd:{_cmd}"}
