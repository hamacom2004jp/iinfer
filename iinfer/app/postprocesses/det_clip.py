from iinfer.app import common, postprocess
from pathlib import Path
from PIL import Image
from typing import Dict, Any, List
import cv2
import logging
import numpy as np


class DetClip(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, image_type:str='capture', clip_margin:int=0):
        """
        Object Detectionの推論結果となったbbox部分を個別の画像として切り出す後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            image_type (str): 切り出した画像のファイル形式
            clip_margin (int): bboxの周囲に余白を設けるピクセル数
            output_dir (Path): 切り出した画像を保存するディレクトリ
        """
        super().__init__(logger)
        self.image_type = image_type
        self.clip_margin = clip_margin

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
        return 'json_connectstr', None, None

    def post_json(self, json_session, outputs:Dict[str, Any], output_image:Image.Image):
        """
        outputsに対して後処理を行う関数です。

        Args:
            json_session (任意): JSONセッション
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_boxes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_boxes\'] must be set.')
        output_boxes = data['output_boxes']

        if output_image is None or "output_image_name" not in outputs:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_image\'] and outputs[\'success\'][\'output_image_shape\'] and outputs[\'success\'][\'output_image_name\'] must be set.')

        output_image_name = Path(outputs["output_image_name"]).stem

        # 切り出し
        result = ''
        for i, box in enumerate(output_boxes):
            y1, x1, y2, x2 = box
            x1 = max(0, np.floor(x1 + 0.5).astype(int) - self.clip_margin)
            y1 = max(0, np.floor(y1 + 0.5).astype(int) - self.clip_margin)
            x2 = min(output_image.width, np.floor(x2 + 0.5).astype(int) + self.clip_margin)
            y2 = min(output_image.height, np.floor(y2 + 0.5).astype(int) + self.clip_margin)

            cropped_image = output_image.crop((x1, y1, x2, y2))
            img_npy = common.img2npy(cropped_image)

            img_b64 = None
            image_name = f"{output_image_name}.{i}.{self.image_type}"
            if self.image_type == 'capture' or self.image_type is None:
                img_b64 = common.npy2b64str(img_npy)
            else:
                img_byte = common.img2byte(cropped_image, format=self.image_type)
                img_b64 = common.bytes2b64str(img_byte)
            result += f'{self.image_type},'+img_b64+f',{img_npy.shape[0]},{img_npy.shape[1]},{img_npy.shape[2] if len(img_npy.shape) > 2 else -1},{image_name}\n'

        return result
    