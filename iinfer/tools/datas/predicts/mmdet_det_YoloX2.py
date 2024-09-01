from iinfer.app.predicts import mmdet_det_YoloX
import logging


SITE = 'https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = True
REQUIREd_MODEL_WEIGHT = False

class MMDetYoloX2(mmdet_det_YoloX.MMDetYoloX):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
