from PIL import Image
from iinfer.app.predicts import det_YoloX
import onnxruntime as rt


def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:Image, labels:list[str]=None, colors:list[tuple[int]]=None):
    return det_YoloX.predict(session, img_width, img_height, image, labels=labels, colors=colors)
