from iinfer.app import postprocess
from iinfer.app.commons import convert
from iinfer.app.injections import after_http_injection
from PIL import Image
from typing import Dict, Any
from urllib3.exceptions import InsecureRequestWarning
import logging
import requests
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)

class Httpreq(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, fileup_name:str='file', json_without_img:bool=False):
        """
        HTTP Requestを行う後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            fileup_name (str, optional): ファイルアップロード名。デフォルトは'file'。
            json_without_img (bool, optional): JSONに画像を含めない場合はTrue。デフォルトはFalse。
        """
        super().__init__(logger, json_without_img)
        self.fileup_name = fileup_name
        self.config = dict(fileup_name=fileup_name, json_without_img=json_without_img)
        self.injection = after_http_injection.AfterHttpInjection(self.config, self.logger)

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
        self.injection._set_config('outputs_url', json_connectstr)
        self.injection._set_config('output_image_url', img_connectstr)
        self.req_session = requests.Session()
        return json_connectstr, img_connectstr, text_connectstr

    def post_text(self, text_session, res_str:str):
        """
        res_strに対して後処理を行う関数です。

        Args:
            text_session (任意): テキストセッション
            res_str (text): 入力テキスト

        Returns:
            str: 後処理結果
        """
        if text_session is None:
            return res_str
        result = self.injection.post_text(text_session, self.req_session, res_str)
        return result

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
        if json_session is None:
            return outputs
        result = self.injection.post_json(json_session, self.req_session, outputs)
        return result

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
        if img_session is None:
            return output_image
        result = self.injection.post_img(img_session, self.req_session, result, output_image)
        return result
