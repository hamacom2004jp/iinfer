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
        json_session = (requests.Session(), json_connectstr)
        img_session = (requests.Session(), img_connectstr)
        text_session = (requests.Session(), text_connectstr)
        return json_session, img_session, text_session

    def post_text(self, text_session, res_str:str):
        """
        res_strに対して後処理を行う関数です。

        Args:
            text_session (任意): テキストセッション
            res_str (text): 入力テキスト

        Returns:
            str: 後処理結果
        """
        if text_session is None or text_session[1] == "":
            return res_str
        res = text_session[0].post(text_session[1], data=res_str, verify=False)
        if res.status_code != 200:
            raise Exception(f"Failed to postprocess. status_code={res.status_code}. res.reason={res.reason} res.text={res.text}")
        try:
            outputs = res.json()
        except:
            outputs = dict(success=res.text)
        return outputs

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
        if json_session is None or json_session[1] == "":
            return outputs
        res = json_session[0].post(json_session[1], json=outputs, verify=False)
        if res.status_code != 200:
            raise Exception(f"Failed to postprocess. status_code={res.status_code}. res.reason={res.reason} res.text={res.text}")
        try:
            outputs = res.json()
        except:
            outputs = dict(success=res.text)
        return outputs

    def post_img(self, img_session, result:Dict[str, Any], output_image:Image.Image):
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
        if img_session is None or img_session[1] == "":
            return output_image
        if self.fileup_name is None:
            raise Exception(f"fileup_name is empty.")
        files = {self.fileup_name: common.img2byte(output_image, "JPEG")}
        res = img_session[0].post(img_session[1], files=files, verify=False)
        if res.status_code != 200:
            raise Exception(f"Failed to postprocess. status_code={res.status_code}. res.reason={res.reason} res.text={res.text}")
        output_image = common.imgbytes2npy(res.content)
        return output_image

