from iinfer.app.predicts import mmpretrain_cls_swin
import logging

SITE = 'https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer'
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
REQUIREd_MODEL_CONF = True
REQUIREd_MODEL_WEIGHT = False

class MMPretrainClsSwinLite(mmpretrain_cls_swin.MMPretrainClsSwin):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)
