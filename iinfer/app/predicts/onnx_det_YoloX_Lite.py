from iinfer.app.predicts import onnx_det_YoloX
import logging


SITE = 'https://github.com/Megvii-BaseDetection/YOLOX/'
IMAGE_WIDTH = 416
IMAGE_HEIGHT = 416
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = True

class OnnxdetYoloXLite(onnx_det_YoloX.OnnxDetYoloX):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
