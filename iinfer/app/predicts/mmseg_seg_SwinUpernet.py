from iinfer.app.predicts.mmseg_seg_PSPNet import MMSegPSPNet
import logging

SITE = 'https://github.com/open-mmlab/mmsegmentation/tree/b040e147adfa027bbc071b624bedf0ae84dfc922/configs/swin'
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
USE_MODEL_CONF = True

class MMSegSwinUpernet(MMSegPSPNet):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
