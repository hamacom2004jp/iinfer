from iinfer.app.predicts import mmdet_det_YoloX
import logging

SITE = 'https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox'
IMAGE_WIDTH = 416
IMAGE_HEIGHT = 416
USE_MODEL_CONF = True

class MMDetYoloXLite(mmdet_det_YoloX.MMDetYoloX):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
