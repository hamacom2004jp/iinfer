from iinfer.app import common
from PIL import Image
from typing import List, Tuple
import numpy as np
import onnxruntime as rt


SITE = 'https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4'
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224

def create_session(model_path:str, model_provider:str, gpu_id:int=None):
    """
    推論セッションを作成する関数です。

    Args:
        model_path (str): モデルファイルのパス
        gpu_id (int, optional): GPU ID. Defaults to None.

    Returns:
        rt.InferenceSession: 推論セッション
    """
    if gpu_id is None:
        session = rt.InferenceSession(model_path, providers=[model_provider])
    else:
        session = rt.InferenceSession(model_path, providers=[model_provider], providers_options=[{'device_id': str(gpu_id)}])
    return session

def predict(session:rt.InferenceSession, img_width:int, img_height:int, image:Image, labels:List[str]=None, colors:List[Tuple[int]]=None):
    """
    予測を行う関数です。

    Args:
        session (rt.InferenceSession): 推論セッション
        img_width (int): モデルのINPUTサイズ（画像の幅）
        img_height (int): モデルのINPUTサイズ（画像の高さ）
        image (Image): 入力画像（RGB配列であること）
        labels (List[str], optional): クラスラベルのリスト. Defaults to None.
        colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.

    Returns:
        Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
    """
    # RGB画像をBGR画像に変換
    img_npy = common.img2npy(image)
    img_npy = common.bgr2rgb(img_npy)

    image_data, _, image_obj = preprocess_img(image, img_width, img_height)

    results = session.run(["Softmax:0"], {"images:0": image_data})[0]

    output_scores, output_classes = [], []
    result = reversed(results[0].argsort()[-5:])
    for r in result:
        output_classes.append(r)
        output_scores.append(results[0][r])

    return dict(output_scores=output_scores, output_classes=output_classes), image_obj

def resize_img(image:Image, to_w, to_h):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    scale = min(to_w/iw, to_h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', (to_w, to_h), (128,128,128))
    new_image.paste(image, ((to_w-nw)//2, (to_h-nh)//2))
    return new_image

def preprocess_img(image:Image, model_img_width:int, model_img_height:int):
    boxed_image = resize_img(image, model_img_width, model_img_height)
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)
    image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
    return image_data, image_size, image
