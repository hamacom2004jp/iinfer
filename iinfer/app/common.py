from PIL import Image, ImageDraw
from typing import List, Tuple
import numpy as np

BASE_MODELS = {}
BASE_BREFORE_INJECTIONS = {}
BASE_AFTER_INJECTIONS = {}
BASE_TRAIN_MODELS = {}


def draw_boxes(image:Image.Image, boxes:List[List[float]], scores:List[float], classes:List[int], ids:List[str]=None,
               labels:List[str]=None, colors:List[Tuple[int]]=None, tracks:List[int]=None,
               nodraw:bool=False, nolookup:bool=False) -> Tuple[Image.Image, List[str]]:
    """
    画像にバウンディングボックスを描画します。

    Args:
        image (Image.Image): 描画する画像
        boxes (List[List[float]]): バウンディングボックスの座標リスト
        scores (List[float]): 各バウンディングボックスのスコアリスト
        classes (List[int]): 各バウンディングボックスのクラスリスト
        ids (List[str]): 各バウンディングボックスのIDリスト
        labels (List[str], optional): クラスのラベルリスト. Defaults to None.
        colors (List[Tuple[int]], optional): クラスごとの色のリスト. Defaults to None.
        tracks (List[int], optional): トラックIDリスト. Defaults to None.
        nodraw (bool, optional): 描画しない場合はTrue. Defaults to False.
        nolookup (bool, optional): ラベル及び色をクラスIDから取得しない場合はTrue. Defaults to False.

    Returns:
        Image: バウンディングボックスが描画された画像
        List[str]: 各バウンディングボックスのラベルリスト
    """
    draw = ImageDraw.Draw(image)
    ids = ids if ids is not None else [None] * len(boxes)
    tracks = tracks if tracks is not None else [None] * len(boxes)
    output_labels = []
    for i, (box, score, cl, id, trc) in enumerate(zip(boxes, scores, classes, ids, tracks)):
        y1, x1, y2, x2 = box
        x1 = max(0, np.floor(x1 + 0.5).astype(int))
        y1 = max(0, np.floor(y1 + 0.5).astype(int))
        x2 = min(image.width, np.floor(x2 + 0.5).astype(int))
        y2 = min(image.height, np.floor(y2 + 0.5).astype(int))
        if not nolookup:
            color = colors[int(cl)] if colors is not None and len(colors) > cl else make_color(str(int(cl)))
            label = str(labels[int(cl)]) if labels is not None else str(id) if id is not None else None
        else:
            color = colors[i] if colors is not None and len(colors) > i else make_color(str(int(cl)))
            label = str(labels[i]) if labels is not None and len(labels) > i else None
        if not nodraw:
            if x2 - x1 > 0 and y2 - y1 > 0:
                draw.rectangle(((x1, y1), (x2, y2)), outline=color)
                if label is not None:
                    draw.rectangle(((x1, y1), (x2, y1+10)), outline=color, fill=color)
                    draw.text((x1, y1), f"{label}:{score}", tuple([int(255-c) for c in color]))
        output_labels.append(label)

    return image, output_labels

def make_color(idstr:str) -> Tuple[int]:
    if len(idstr) < 3:
        idstr = idstr.zfill(3)
    return tuple([ord(c) * ord(c) % 256 for c in idstr[:3]])
