from iinfer.app import common
import platform
import logging

class Redis(object):
    def __init__(self, logger: logging.Logger, wsl_name: str = None, wsl_user: str = None):
        self.logger = logger
        self.wsl_name = wsl_name
        self.wsl_user = wsl_user

    def docker_run(self, port: int, password: str):
        if port is None is None:
            return {"warn":f"port option is required."}
        if password is None:
            return {"warn":f"password option is required."}
        if platform.system() == 'Windows':
            if self.wsl_name is None:
                return {"warn":f"wsl_name option is required."}
            if self.wsl_user is None:
                return {"warn":f"wsl_user option is required."}
            code, _ = common.cmd(f"wsl -d {self.wsl_name} -u {self.wsl_user} docker run -it --name redis --rm -e TZ=UTC -p {port}:{port} -e REDIS_PASSWORD={password} ubuntu/redis:latest",
                                self.logger)
            return {"output":code}
        elif platform.system() == 'Linux':
            code, _ = common.cmd(f"docker run -it --name redis --rm -e TZ=UTC -p {port}:{port} -e REDIS_PASSWORD={password} ubuntu/redis:latest", self.logger)
            return {"output":code}
        else:
            return {"warn":f"Unsupported platform."}

    def docker_stop(self):
        if platform.system() == 'Windows':
            if self.wsl_name is None:
                return {"warn":f"wsl_name option is required."}
            if self.wsl_user is None:
                return {"warn":f"wsl_user option is required."}
            code, _ = common.cmd(f"wsl -d {self.wsl_name} -u {self.wsl_user} docker stop redis", self.logger)
            common.cmd(f"wsl --shutdown", self.logger)
            return {"output":code}
        elif platform.system() == 'Linux':
            code, _ = common.cmd(f"docker stop redis", self.logger)
            return {"output":code}
        else:
            return {"warn":f"Unsupported platform."}
