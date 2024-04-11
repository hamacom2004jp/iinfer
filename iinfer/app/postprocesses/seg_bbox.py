from iinfer.app import common, postprocess
from iinfer.app.commons import convert
from iinfer.app.injections import after_seg_bbox_injection
from PIL import Image
from typing import Dict, Any, List
import cv2
import logging

class SegBBox(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, del_segments:bool=True, nodraw:bool=False, nodraw_bbox:bool=False, nodraw_rbbox:bool=False, output_preview:bool=False):
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

    def create_session(self, json_connectstr:str, img_connectstr:str, text_connectstr:str):
        """
        後処理のセッションを作成する関数です。
        ここで後処理準備を完了するようにしてください。
        戻り値の後処理セッションの型は問いません。

        Args:
            json_connectstr (str): 推論結果後処理のセッション確立に必要な接続文字列
            img_connectstr (str): 可視化画像後処理のセッション確立に必要な接続文字列
            text_connectstr (str): テキストデータ処理のセッション確立に必要な接続文字列

        Returns:
            推論結果後処理のセッション
            可視化画像後処理のセッション
            テキストデータ処理のセッション
        """
        return 'json_connectstr', 'img_connectstr', None

    def post_json(self, json_session, outputs:Dict[str, Any], output_image:Image.Image) -> Dict[str, Any]:
        """
        outputsに対して後処理を行う関数です。
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
            json_session (任意): JSONセッション
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
        """
        outputs = self.injection.post_json(outputs)
        data = outputs['success']
        return data

    def post_img(self, img_session, result:Dict[str, Any], output_image:Image.Image) -> Image.Image:
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。

        Args:
            img_session (任意): 画像セッション
            result (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Image: 後処理結果
        """
        output_image = self.injection.post_img(dict(success=result), output_image)

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
        return output_image
