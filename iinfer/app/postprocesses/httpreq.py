from iinfer.app import common, postprocess
from PIL import Image
from typing import Dict, Any
import logging
import requests

class Httpreq(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, fileup_name:str='file'):
        """
        HTTP Requestを行う後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
        """
        super().__init__(logger)
        self.fileup_name = fileup_name
        import urllib3
        from urllib3.exceptions import InsecureRequestWarning
        urllib3.disable_warnings(InsecureRequestWarning)

    def post_json(self, json_connectstr,  outputs:Dict[str, Any]):
        """
        outputsに対して後処理を行う関数です。

        Args:
            json_connectstr (str): 推論結果の後処理に必要な接続文字列
            outputs (Dict[str, Any]): 推論結果

        Returns:
            Dict[str, Any]: 後処理結果
        """
        if json_connectstr is None or json_connectstr == "":
            raise Exception(f"json_connectstr is empty.")
        json_session = requests.Session()
        res = json_session.post(json_connectstr, json=outputs, verify=False)
        if res.status_code != 200:
            raise Exception(f"Failed to postprocess. status_code={res.status_code}. res.reason={res.reason} res.text={res.text}")
        try:
            outputs = res.json()
        except:
            outputs = dict(success=res.text)
        return outputs

    def post_img(self, img_connectstr:str, outputs:Dict[str, Any], output_image:Image.Image):
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
        if img_connectstr is None or img_connectstr == "":
            return output_image
        img_session = requests.Session()
        if self.fileup_name is None:
            raise Exception(f"fileup_name is empty.")
        files = {self.fileup_name: common.img2byte(output_image, "JPEG")}
        res = img_session.post(img_connectstr, files=files, verify=False)
        if res.status_code != 200:
            raise Exception(f"Failed to postprocess. status_code={res.status_code}. res.reason={res.reason} res.text={res.text}")
        output_image = common.imgbytes2npy(res.content)
        return output_image

