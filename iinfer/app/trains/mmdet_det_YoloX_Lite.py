from iinfer.app.trains import mmdet_det_YoloX
import logging


SITE = 'https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox'

class MMDetYoloXLite(mmdet_det_YoloX.MMDetYoloX):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
