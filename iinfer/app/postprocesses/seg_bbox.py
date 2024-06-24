from iinfer.app import postprocess
from iinfer.app.commons import convert
from iinfer.app.injections import after_seg_bbox_injection
from PIL import Image
from typing import Dict, Tuple, Any
import cv2
import logging

class SegBBox(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, del_segments:bool=True, nodraw:bool=False, nodraw_bbox:bool=False, nodraw_rbbox:bool=False,
                 output_preview:bool=False):
        """
        Segmentationの推論結果をフィルタリングする後処理クラスです。
        閾値に満たない推論結果を除外します。
        
        Args:
            logger (logging.Logger): ロガー
            del_segments (bool): セグメントを削除する
            nodraw (bool): 描画しない
            nodraw_bbox (bool): バウンディングボックスを描画しない
            nodraw_rbbox (bool): 回転バウンディングボックスを描画しない
            output_preview (bool): プレビューを出力する
        """
        super().__init__(logger)
        self.config = dict(nodraw=nodraw, nodraw_bbox=nodraw_bbox, nodraw_rbbox=nodraw_rbbox, del_segments=del_segments, output_preview=output_preview)
        self.injection = after_seg_bbox_injection.AfterSegBBoxInjection(self.config, self.logger)

    def post(self, outputs:Dict[str, Any], output_image:Image.Image) -> Tuple[Dict[str, Any], Image.Image]:
        """
        後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_sem_seg': str,
                'output_sem_seg_shape': List[int],
                'output_sem_seg_dtype': str,
                'output_classes': List[int],
                'output_labels': List[str],
                'output_palette': List[int]
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
