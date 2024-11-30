from cmdbox.app import common
from iinfer import version
from pathlib import Path
import getpass
import logging
import os
import platform
import shutil
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
            returncode, _ = common.cmd(f"wsl -d {self.wsl_name} -u {self.wsl_user} {cmd}", self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install redis-server.")
                return {"error": f"Failed to install redis-server."}
            return {"success": f"Success to install redis-server."}

        elif platform.system() == 'Linux':
            returncode, _ = common.cmd(f"{cmd}", self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install redis-server.")
                return {"error": f"Failed to install redis-server."}
            return {"success": f"Success to install redis-server."}

        else:
            return {"warn":f"Unsupported platform."}

    def server(self, data:Path, install_iinfer_tgt:str='iinfer', install_onnx:bool=True,
               install_mmdet:bool=True, install_mmseg:bool=True, install_mmcls:bool=False, install_mmpretrain:bool=True,
               install_insightface=False, install_from:str=None, install_no_python:bool=False, install_tag:str=None, install_use_gpu:bool=False):
        if platform.system() == 'Windows':
            return {"warn": f"Build server command is Unsupported in windows platform."}
        from importlib.resources import read_text
        user = getpass.getuser()
        install_tag = f"_{install_tag}" if install_tag is not None else ''
        with open('Dockerfile', 'w', encoding='utf-8') as fp:
            text = read_text(f'iinfer.docker', 'Dockerfile')
            wheel = Path(install_iinfer_tgt)
            if wheel.exists() and wheel.suffix == '.whl':
                shutil.copy(wheel, Path('.').resolve() / wheel.name)
                #install_iinfer = f'/home/{user}/{wheel.name}'
                install_iinfer_tgt = f'/home/{user}/{wheel.name}'
                text = text.replace('#{COPY_IINFER}', f'COPY {wheel.name} {install_iinfer_tgt}')
            else:
                text = text.replace('#{COPY_IINFER}', '')

            start_sh_src = Path(__file__).parent.parent / 'docker' / 'scripts'
            #start_sh_tgt = f'/home/{user}/scripts'
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
            text = text.replace('#{INSTALL_PYTHON}', f'RUN apt-get update && apt-get install -y python3.11 python3.11-distutils python3-pip python-is-python3' if not install_no_python else '')
            text = text.replace('#{INSTALL_TAG}', install_tag)
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
            returncode, _ = common.cmd(f"{cmd}", self.logger, slise=-1)
            #os.remove('Dockerfile')
            if returncode != 0:
                self.logger.warning(f"Failed to install iinfer-server.")
                return {"error": f"Failed to install iinfer-server."}
            return {"success": f"Success to install iinfer-server. and docker-compose.yml is copied."}

        else:
            return {"warn":f"Unsupported platform."}

    def onnx(self, install_use_gpu:bool=False):
        returncode, _ = common.cmd('pip install onnxruntime', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install onnxruntime.")
            return {"error": f"Failed to install onnxruntime."}
        if install_use_gpu:
            returncode, _ = common.cmd('pip install onnxruntime-gpu', logger=self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install onnxruntime-gpu.")
                return {"error": f"Failed to install onnxruntime-gpu."}
        return {"success": f"Success to install onnxruntime."}

    def insightface(self, data_dir: Path, install_use_gpu:bool=False):
        returncode, _ = common.cmd('pip install cython', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install cython.")
            return {"error": f"Failed to install cython."}
        ret = self.onnx(install_use_gpu)
        if "error" in ret: return ret
        returncode, _ = common.cmd('python -m pip install --upgrade pip setuptools', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install setuptools.")
            return {"error": f"Failed to install setuptools."}
        returncode, _ = common.cmd('pip install insightface', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install insightface.")
            return {"error": f"Failed to install insightface."}
        return {"success": f"Success to install insightface."}

    def _torch(self, install_use_gpu:bool=False):
        if install_use_gpu:
            returncode, _ = common.cmd('pip install numpy==1.26.3 torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118', logger=self.logger, slise=-1)
        else:
            returncode, _ = common.cmd('pip install numpy==1.26.3 torch==2.1.0 torchvision torchaudio', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install torch torchvision torchaudio.")
            return {"error": f"Failed to install torch torchvision torchaudio."}
        return {"success": f"Success to install torch torchvision torchaudio."}

    def _openmin(self, install_use_gpu:bool=False):
        returncode, _ = common.cmd('pip install openmim', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install openmim.")
            return {"error": f"Failed to install openmim."}
        return {"success": f"Success to install openmim."}

    def _mmcv(self, install_use_gpu:bool=False):
        if install_use_gpu:
            returncode, _ = common.cmd('pip install mmcv==2.1.0 -f https://download.openmmlab.com/mmcv/dist/cu118/torch2.1/index.html', logger=self.logger, slise=-1)
            if returncode != 0:
                self.logger.warning(f"Failed to install mmcv.")
                return {"error": f"Failed to install mmcv."}
        else:
            returncode, _ = common.cmd('mim install mmcv>=2.0.0', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install mmcv.")
            return {"error": f"Failed to install mmcv."}
        return {"success": f"Success to install mmcv."}

    def _transformers(self, install_use_gpu:bool=False):
        returncode, _ = common.cmd('pip install accelerate transformers bitsandbytes sentence-transformers', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install accelerate transformers bitsandbytes sentence-transformers.")
            return {"error": f"Failed to install accelerate transformers bitsandbytes sentence-transformers."}
        return {"success": f"Success to install accelerate transformers bitsandbytes sentence-transformers."}

    def mmdet(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _ = common.cmd(f'git clone https://github.com/open-mmlab/mmdetection.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmdetection. Delete mmdetection as it probably already exists.")
            return {"error": f"Failed to git clone mmdetection. Delete mmdetection as it probably already exists."}
        srcdir = Path('.') / 'mmdetection'
        shutil.copytree(srcdir, data_dir / 'mmdetection', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _ = common.cmd('mim install mmengine mmdet', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmdet.")
            return {"error": f"Failed to install mmengine mmdet."}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmdetection'}' manually."}
        return {"success": f"Success to install mmdet."}

    def mmseg(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _ = common.cmd(f'git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists.")
            return {"error": f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists."}
        srcdir = Path('.') / 'mmsegmentation'
        shutil.copytree(srcdir, data_dir / 'mmsegmentation', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _ = common.cmd('mim install mmengine mmsegmentation', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmsegmentation.")
            return {"error": f"Failed to install mmengine mmsegmentation."}

        ret, _ = common.cmd('pip install ftfy', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install ftfy.")
            return {"error": f"Failed to install ftfy."}

        ret, _ = common.cmd('pip install regex', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install regex.")
            return {"error": f"Failed to install regex."}

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

        ret, _ = common.cmd('mim install mmengine mmcls', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmengine mmcls.")
            return {"error": f"Failed to install mmengine mmcls."}

        return {"success": f"Success to install mmcls."}

    def mmpretrain(self, data_dir:Path, install_use_gpu:bool=False):
        returncode, _ = common.cmd(f'git clone https://github.com/open-mmlab/mmpretrain.git', logger=self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to git clone mmpretrain. Delete mmpretrain as it probably already exists.")
            return {"error": f"Failed to git clone mmpretrain. Delete mmpretrain as it probably already exists."}
        srcdir = Path('.') / 'mmpretrain'
        shutil.copytree(srcdir, data_dir / 'mmpretrain', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._torch(install_use_gpu)
        if "error" in ret: return ret
        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret

        ret, _ = common.cmd('mim install mmengine mmpretrain', logger=self.logger, slise=-1)
        if ret != 0:
            self.logger.warning(f"Failed to install mmpretrain.")
            return {"error": f"Failed to install mmpretrain."}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir}' manually."}
        return {"success": f"Success to install mmpretrain."}
