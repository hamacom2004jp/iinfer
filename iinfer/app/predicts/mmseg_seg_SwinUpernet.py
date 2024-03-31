from iinfer.app.predicts.mmseg_seg_PSPNet import MMSegPSPNet
import logging

SITE = 'https://github.com/open-mmlab/mmsegmentation/tree/main/configs/swin'
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
REQUIREd_MODEL_CONF = True
REQUIREd_MODEL_WEIGHT = False

class MMSegSwinUpernet(MMSegPSPNet):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
