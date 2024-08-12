from iinfer.app.trains import mmseg_seg_PSPNet
import logging


SITE = 'https://github.com/open-mmlab/mmsegmentation/tree/main/configs/swin'

class MMSegSwinUpernet(mmseg_seg_PSPNet.MMSegPSPNet):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
