from iinfer.app import common
import logging

class Install(object):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def onnx(self):
        returncode, _ = common.cmd('pip install onnxruntime', logger=self.logger)
        if returncode != 0:
            common.print_format({"warn":f"Failed to install onnxruntime."}, format, tm)
            self.logger.error(f"Failed to install onnxruntime.")
            return {"error": f"Failed to install onnxruntime."}
        return {"success": f"Success to install onnxruntime."}

    def mmdet(self):
        returncode, _ = common.cmd('pip install torch torchvision openmim', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install torch.")
            return {"error": f"Failed to install torch."}

        returncode, _ = common.cmd('mim install mmengine mmcv mmdet', logger=self.logger)
        if returncode != 0:
            self.logger.error(f"Failed to install mmengine.")
            return {"error": f"Failed to install mmengine."}

        return {"success": f"Success to install mmdet."}
