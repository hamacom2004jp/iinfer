from iinfer.app.predicts import mmpretrain_cls_swin

SITE = 'https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer'
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
USE_MODEL_CONF = True

class MMPretrainClsSwinLite(mmpretrain_cls_swin.MMPretrainClsSwin):
    pass
