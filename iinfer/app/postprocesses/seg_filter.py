from cmdbox.app.commons import convert
from iinfer.app import postprocess
from iinfer.app.injections import after_seg_filter_injection
from PIL import Image
from typing import Dict, Tuple, Any, List
import cv2
import logging


class SegFilter(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, logits_th:float=-100.0, classes:List[int]=None, labels:List[str]=None, nodraw:bool=False, del_logits:bool=True):
        """
        Segmentationの推論結果をフィルタリングする後処理クラスです。
        閾値に満たない推論結果を除外します。
        
        Args:
            logger (logging.Logger): ロガー
            logits_th (float): スコアの閾値
            classes (List[int]): クラスのリスト
            labels (List[str]): ラベルのリスト
            nodraw (bool): 描画しない
            del_logits (bool): スコア要素を削除する
        """
        super().__init__(logger)
        self.config = dict(logits_th=logits_th, classes=classes, labels=labels, nodraw=nodraw, del_logits=del_logits)
        self.injection = after_seg_filter_injection.AfterSegFilterInjection(self.config, self.logger)

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
