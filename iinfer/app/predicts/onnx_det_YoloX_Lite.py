from PIL import Image
from iinfer.app.predicts import onnx_det_YoloX
from typing import List, Tuple
import onnxruntime as rt


SITE = 'https://github.com/Megvii-BaseDetection/YOLOX/'
IMAGE_WIDTH = 416
IMAGE_HEIGHT = 416

def create_session(model_path:str, model_provider:str, gpu_id:int=None):
    """
    推論セッションを作成する関数です。

    Args:
        model_path (str): モデルファイルのパス
        gpu_id (int, optional): GPU ID. Defaults to None.

    Returns:
        rt.InferenceSession: 推論セッション
    """
    return onnx_det_YoloX.create_session(model_path, model_provider, gpu_id)

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
        Tuple[Dict[str, Any], Image]: 予測結果と出力画像のタプル
    """
    return det_YoloX.predict(session, img_width, img_height, image, labels=labels, colors=colors)
