from iinfer import version
from iinfer.app import common
from pathlib import Path
import getpass
import logging
import os
import platform
import shutil

class Install(object):
    def __init__(self, logger: logging.Logger, wsl_name: str = None, wsl_user: str = None):
        self.logger = logger
        self.wsl_name = wsl_name
        self.wsl_user = wsl_user

    def redis(self):
        cmd = f"docker pull ubuntu/redis:latest"
        if platform.system() == 'Windows':
            if self.wsl_name is None:
                return {"warn":f"wsl_name option is required."}
            if self.wsl_user is None:
                return {"warn":f"wsl_user option is required."}
            returncode, _ = common.cmd(f"wsl -d {self.wsl_name} -u {self.wsl_user} {cmd}", self.logger)
            if returncode != 0:
                self.logger.error(f"Failed to install redis-server.")
                return {"error": f"Failed to install redis-server."}
            return {"success": f"Success to install redis-server."}

        elif platform.system() == 'Linux':
            returncode, _ = common.cmd(f"{cmd}", self.logger)
            if returncode != 0:
                self.logger.error(f"Failed to install redis-server.")
                return {"error": f"Failed to install redis-server."}
            return {"success": f"Success to install redis-server."}

        else:
            return {"warn":f"Unsupported platform."}

    def server(self, install_iinfer:str='iinfer', install_onnx:bool=True, install_mmdet:bool=True, install_mmcls:bool=False, install_mmpretrain:bool=True, install_mmrotate:bool=True):
        if platform.system() == 'Windows':
            return {"warn": f"Build server command is Unsupported in windows platform."}
        from importlib.resources import read_text
        user = getpass.getuser()
        with open('Dockerfile', 'w', encoding='utf-8') as fp:
            text = read_text(f'{common.APP_ID}.docker', 'Dockerfile')
            text = text.replace('${MKUSER}', user)
            text = text.replace('${INSTALL_IINFER}', install_iinfer)
            text = text.replace('#{INSTALL_ONNX}', f'RUN iinfer -m install -c onnx --data /home/{user}/.iinfer' if install_onnx else '')
            text = text.replace('#{INSTALL_MMDET}', f'RUN iinfer -m install -c mmdet --data /home/{user}/.iinfer' if install_mmdet else '')
            text = text.replace('#{INSTALL_MMCLS}', f'RUN iinfer -m install -c mmcls --data /home/{user}/.iinfer' if install_mmcls else '')
            text = text.replace('#{INSTALL_MMPRETRAIN}', f'RUN iinfer -m install -c mmpretrain --data /home/{user}/.iinfer' if install_mmpretrain else '')
            text = text.replace('#{INSTALL_MMROTATE}', f'RUN iinfer -m install -c mmrotate --data /home/{user}/.iinfer' if install_mmrotate else '')
            fp.write(text)
        with open('docker-compose.yml', 'w', encoding='utf-8') as fp:
            text = read_text(f'{common.APP_ID}.docker', 'docker-compose.yml')
            text = text.replace('${VERSION}', version.__version__)
            fp.write(text)
        cmd = f'docker build -t hamacom/iinfer:{version.__version__} -f Dockerfile .'

        if platform.system() == 'Linux':
            returncode, _ = common.cmd(f"{cmd}", self.logger, True)
            os.remove('Dockerfile')
            if returncode != 0:
                self.logger.error(f"Failed to install iinfer-server.")
                return {"error": f"Failed to install iinfer-server."}
            return {"success": f"Success to install iinfer-server. and docker-compose.yml is copied."}

        else:
            return {"warn":f"Unsupported platform."}

    def onnx(self):
        returncode, _ = common.cmd('pip install onnxruntime', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install onnxruntime.")
            return {"error": f"Failed to install onnxruntime."}
        return {"success": f"Success to install onnxruntime."}

    def mmdet(self, data_dir: Path):
        returncode, _ = common.cmd(f'git clone https://github.com/open-mmlab/mmdetection.git', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to git clone mmdetection.")
            return {"error": f"Failed to git clone mmdetection."}
        srcdir = Path('.') / 'mmdetection'
        shutil.copytree(srcdir, data_dir / 'mmdetection', dirs_exist_ok=True)
        shutil.rmtree(srcdir, ignore_errors=True)

        returncode, _ = common.cmd('pip install torch torchvision openmim', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install torch.")
            return {"error": f"Failed to install torch."}

        returncode, _ = common.cmd('mim install mmengine mmcv mmdet', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install mmdet.")
            return {"error": f"Failed to install mmdet."}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmdetection'}' manually."}
        return {"success": f"Success to install mmdet."}

    def mmrotate(self, data_dir: Path):
        returncode, _ = common.cmd(f'git clone https://github.com/open-mmlab/mmrotate.git', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to git clone mmrotate.")
            return {"error": f"Failed to git clone mmrotate."}
        srcdir = Path('.') / 'mmrotate'
        shutil.copytree(srcdir, data_dir / 'mmrotate', dirs_exist_ok=True)
        shutil.rmtree(srcdir, ignore_errors=True)

        returncode, _ = common.cmd('pip install torch torchvision openmim', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install torch.")
            return {"error": f"Failed to install torch."}

        returncode, _ = common.cmd('mim install mmengine mmcv mmdet mmrotate', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install mmrotate.")
            return {"error": f"Failed to install mmrotate."}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmrotate'}' manually."}
        return {"success": f"Success to install mmrotate."}

    def mmcls(self):
        returncode, _ = common.cmd('pip install torch torchvision openmim', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install torch.")
            return {"error": f"Failed to install torch."}

        returncode, _ = common.cmd('mim install mmengine mmcv mmcls', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install mmcls.")
            return {"error": f"Failed to install mmcls."}

        return {"success": f"Success to install mmcls."}

    def mmpretrain(self, data_dir: Path):
        returncode, _ = common.cmd(f'git clone https://github.com/open-mmlab/mmpretrain.git', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to git clone mmpretrain.")
            return {"error": f"Failed to git clone mmpretrain."}
        srcdir = Path('.') / 'mmpretrain'
        shutil.copytree(srcdir, data_dir / 'mmpretrain', dirs_exist_ok=True)
        shutil.rmtree(srcdir, ignore_errors=True)

        returncode, _ = common.cmd('pip install torch torchvision openmim', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install torch.")
            return {"error": f"Failed to install torch."}

        returncode, _ = common.cmd('pip uninstall -y mmcv', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to uninstall mmcv.")
            return {"error": f"Failed to uninstall mmcv."}

        returncode, _ = common.cmd('mim install mmengine mmcv>=2.0.0 mmpretrain', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install mmpretrain.")
            return {"error": f"Failed to install mmpretrain."}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir}' manually."}
        return {"success": f"Success to install mmpretrain."}
