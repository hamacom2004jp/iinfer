from cmdbox.app.commons import convert
from iinfer.app import postprocess
from iinfer.app.injections import after_det_jadge_injection
from PIL import Image
from typing import Dict, Any, Tuple, List
import cv2
import logging


class DetJadge(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger,
                 ok_score_th:float=None, ok_classes:List[int]=None, ok_labels:List[str]=None,
                 ng_score_th:float=None, ng_classes:List[int]=None, ng_labels:List[str]=None,
                 ext_score_th:float=None, ext_classes:List[int]=None, ext_labels:List[str]=None,
                 nodraw:bool=False, output_preview:bool=False):
        """
        Object Detection推論結果のクラススコア元に、この画像としてOK/NG/Grayの判定結果を追加する後処理クラスです。

        Args:
            logger (logging.Logger): ロガー
            ok_score_th (float): ok判定確定のスコアの閾値
            ok_classes (List[int]): ok判定確定のクラスのリスト
            ok_labels (List[str]): ok判定確定のラベルのリスト
            ng_score_th (float): ng判定確定のスコアの閾値
            ng_classes (List[int]): ng判定確定のクラスのリスト
            ng_labels (List[str]): ng判定確定のラベルのリスト
            ext_score_th (float): gray判定確定のスコアの閾値
            ext_classes (List[int]): gray判定確定のクラスのリスト
            ext_labels (List[str]): gray判定確定のラベルのリスト
            nodraw (bool): 描画しない
            output_preview (bool): プレビューを出力する
        """
        super().__init__(logger)
        self.config = dict(ok_score_th=ok_score_th, ok_classes=ok_classes, ok_labels=ok_labels,
                           ng_score_th=ng_score_th, ng_classes=ng_classes, ng_labels=ng_labels,
                           ext_score_th=ext_score_th, ext_classes=ext_classes, ext_labels=ext_labels,
                           nodraw=nodraw, output_preview=output_preview)
        self.injection = after_det_jadge_injection.AfterDetJadgeInjection(self.config, self.logger)

    def post(self, outputs:Dict[str, Any], output_image:Image.Image) -> Tuple[Dict[str, Any], Image.Image]:
        """
        後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_ids': List[int],
                'output_scores': List[float],
                'output_classes': List[int],
                'output_labels': List[str],
                'output_boxes': List[List[int]],
                'output_tracks': List[int]
            }
        }

        Args:
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
            Image: 後処理結果
        """
        outputs, output_image = self.injection.action(None, None, outputs, output_image, None)
        output_preview = self.injection.get_config('output_preview', False)
        if output_preview:
            # RGB画像をBGR画像に変換
            img_npy = convert.img2npy(output_image).copy()
            img_npy = convert.bgr2rgb(img_npy)
            try:
                cv2.imshow('preview', img_npy)
                cv2.waitKey(1)
            except KeyboardInterrupt:
                pass
        return outputs, output_image
