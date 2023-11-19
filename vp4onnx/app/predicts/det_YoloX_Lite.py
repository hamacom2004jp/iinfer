from PIL import Image
from vp4onnx.app.predicts import det_Yolox
import onnxruntime as rt


def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:Image):
    return det_Yolox.predict(session, img_width, img_height, image)
