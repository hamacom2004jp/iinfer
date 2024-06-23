from iinfer.app import postprocess
from iinfer.app.commons import convert
from iinfer.app.injections import after_det_filter_injection
from PIL import Image
from typing import Dict, Any, Tuple, List
import cv2
import logging

class DetFilter(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, score_th:float=0.0, width_th:int=0, height_th:int=0, classes:List[int]=None, labels:List[str]=None,
                 nodraw:bool=False, output_preview:bool=False, json_without_img:bool=False):
        """
        Object Detectionの推論結果をフィルタリングする後処理クラスです。
        閾値に満たない推論結果を除外します。
        
        Args:
            logger (logging.Logger): ロガー
            score_th (float): スコアの閾値
            width_th (int): ボックスの幅の閾値
            height_th (int): ボックスの高さの閾値
            classes (List[int]): クラスのリスト
            labels (List[str]): ラベルのリスト
            nodraw (bool): 描画しない
            output_preview (bool): プレビューを出力する
            json_without_img (bool): JSONに画像を含めない場合はTrue。デフォルトはFalse。
        """
        super().__init__(logger, json_without_img)
        self.config = dict(score_th=score_th, width_th=width_th, height_th=height_th,
                           classes=classes, labels=labels, nodraw=nodraw, output_preview=output_preview)
        self.injection = after_det_filter_injection.AfterDetFilterInjection(self.config, self.logger)

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
