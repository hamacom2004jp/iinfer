from PIL import Image
from iinfer.app.predicts import det_YoloX
from typing import List, Tuple
import onnxruntime as rt


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
