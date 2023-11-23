from PIL import Image
from iinfer.app import common
from typing import List, Tuple
import cv2
import numpy as np
import onnxruntime as rt


SITE = 'https://github.com/Megvii-BaseDetection/YOLOX/'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640

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

    input_shape = (img_width, img_height)
    img, ratio = preprocess(img_npy, input_shape)

    output = session.run(None, {session.get_inputs()[0].name: img[None, :, :, :]})
    predictions = postprocess(output[0], input_shape)[0]
    boxes = predictions[:, :4]
    scores = predictions[:, 4:5] * predictions[:, 5:]
    boxes_xyxy = np.ones_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2]/2.
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3]/2.
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2]/2.
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3]/2.
    boxes_xyxy /= ratio

    dets = multiclass_nms(boxes_xyxy, scores, nms_thr=0.45, score_thr=0.1)
    if dets is not None:
        final_boxes, final_scores, final_cls_inds = dets[:, :4], dets[:, 4], dets[:, 5]
        final_boxes = [[row[1],row[0],row[3],row[2]] for row in final_boxes]
        output_image = common.draw_boxes(image, final_boxes, final_scores, final_cls_inds, labels=labels, colors=colors)

        return dict(output_boxes=final_boxes, output_scores=final_scores, output_classes=final_cls_inds), output_image


def preprocess(img, input_size, swap=(2, 0, 1)):
    """
    画像を前処理する関数です。

    Args:
        img (numpy.ndarray): 入力画像（BGR）
        input_size (tuple): リサイズ後の画像サイズ
        swap (tuple, optional): チャンネルの順番を変更するためのタプル (デフォルト値: (2, 0, 1))

    Returns:
        numpy.ndarray: 前処理された画像
        float: リサイズ倍率
    """
    if len(img.shape) == 3:
        padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
    else:
        padded_img = np.ones(input_size, dtype=np.uint8) * 114

    r = min(input_size[0] / img.shape[0], input_size[1] / img.shape[1])
    resized_img = cv2.resize(
        img,
        (int(img.shape[1] * r), int(img.shape[0] * r)),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)
    padded_img[: int(img.shape[0] * r), : int(img.shape[1] * r)] = resized_img

    padded_img = padded_img.transpose(swap)
    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r

def postprocess(outputs, img_size, p6=False):
    """
    推論結果を後処理する関数です。

    Args:
        outputs (numpy.ndarray): 推論結果の配列
        img_size (tuple): 入力画像のサイズ (height, width)
        p6 (bool, optional): P6モードのフラグ (デフォルトはFalse)

    Returns:
        numpy.ndarray: 後処理された推論結果の配列
    """
    grids = []
    expanded_strides = []
    strides = [8, 16, 32] if not p6 else [8, 16, 32, 64]

    hsizes = [img_size[0] // stride for stride in strides]
    wsizes = [img_size[1] // stride for stride in strides]

    for hsize, wsize, stride in zip(hsizes, wsizes, strides):
        xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))
        grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        expanded_strides.append(np.full((*shape, 1), stride))

    grids = np.concatenate(grids, 1)
    expanded_strides = np.concatenate(expanded_strides, 1)
    outputs[..., :2] = (outputs[..., :2] + grids) * expanded_strides
    outputs[..., 2:4] = np.exp(outputs[..., 2:4]) * expanded_strides

    return outputs

def multiclass_nms(boxes, scores, nms_thr, score_thr):
    """
    多クラスのNon-Maximum Suppression（NMS）を実行し、結果を返す関数です。

    Args:
        boxes (numpy.ndarray): バウンディングボックスの座標情報が格納された配列
        scores (numpy.ndarray): 各バウンディングボックスのクラススコアが格納された配列
        nms_thr (float): NMSの閾値
        score_thr (float): スコアの閾値

    Returns:
        numpy.ndarray: NMSを実行した結果のバウンディングボックスとスコアの配列
    """
    cls_inds = scores.argmax(1)
    cls_scores = scores[np.arange(len(cls_inds)), cls_inds]

    valid_score_mask = cls_scores > score_thr
    if valid_score_mask.sum() == 0:
        return None
    valid_scores = cls_scores[valid_score_mask]
    valid_boxes = boxes[valid_score_mask]
    valid_cls_inds = cls_inds[valid_score_mask]
    keep = nms(valid_boxes, valid_scores, nms_thr)
    if keep:
        dets = np.concatenate(
            [valid_boxes[keep], valid_scores[keep, None], valid_cls_inds[keep, None]], 1
        )
    return dets

def nms(boxes, scores, nms_thr):
    """
    Non-Maximum Suppression (NMS)を実行し、重複するボックスを削除します。

    Args:
        boxes (numpy.ndarray): ボックスの座標情報を含む2次元配列。
        scores (numpy.ndarray): ボックスのスコアを含む1次元配列。
        nms_thr (float): NMSの閾値。

    Returns:
        keep (list): NMSを通過したボックスのインデックスのリスト。
    """
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= nms_thr)[0]
        order = order[inds + 1]

    return keep
