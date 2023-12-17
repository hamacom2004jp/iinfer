from iinfer.app import common, client, postprocess
from PIL import Image
from typing import Dict, Any
import csv
import io
import logging
import requests

class Csv(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, out_header:bool=True):
        """
        JSONをCSVに変換する後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            out_header (bool, optional): ヘッダーを出力するかどうか. Defaults to True.
        """
        super().__init__(logger)
        self.out_header = out_header

    def post_json(self, json_connectstr,  outputs:Dict[str, Any]):
        """
        outputsに対して後処理を行う関数です。

        Args:
            json_connectstr (str): 使用しないパラメーター
            outputs (Dict[str, Any]): 推論結果

        Returns:
            Dict[str, Any]: 後処理結果
        """
        def _to_csv(data, buffer):
            if type(data) == dict:
                if self.out_header:
                    csv.DictWriter(buffer, fieldnames=data.keys()).writeheader()
                else:
                    csv.DictWriter(buffer).writerow(data)
            elif type(data) == list:
                csv.writer(buffer).writerow(data)
            else:
                buffer.write(str(data))
                buffer.write("\n")

        result = ''
        if 'success' in outputs and type(outputs['success']) == list:
            buffer = io.StringIO()
            for data in outputs['success']:
                _to_csv(data, buffer)
            result = buffer.getvalue().strip()
            buffer.close()

        elif 'success' in outputs and type(outputs['success']) == dict:
            buffer = io.StringIO()
            writer = csv.writer(buffer)
            if self.out_header:
                writer.writerow(outputs['success'].keys())
            writer.writerow(outputs['success'].values())
            result = buffer.getvalue().strip()
            buffer.close()

        elif type(outputs) == list:
            buffer = io.StringIO()
            for data in outputs:
                _to_csv(data, buffer)
            result = buffer.getvalue().strip()
            buffer.close()

        else:
            buffer = io.StringIO()
            csv.writer(buffer).writerow(outputs)
            result = buffer.getvalue().strip()
            buffer.close()

        self.out_header = False
        return result

    def post_img(self, img_connectstr:str, outputs:Dict[str, Any], output_image:Image):
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。

        Args:
            img_connectstr (str): 可視化画像の後処理に必要な接続文字列
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image): 入力画像（RGB配列であること）

        Returns:
            Image: 後処理結果
        """
        return output_image
