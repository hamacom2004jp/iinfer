from iinfer.app import postprocess
from iinfer.app.injections import after_showimg_injection
from PIL import Image
from typing import Dict, Tuple, Any
from urllib3.exceptions import InsecureRequestWarning
import logging
import requests
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)

class Showimg(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, host:str='localhost', port:int=6379, password:str='password', svname:str='server', maxrecsize:int=1000):
        """
        推論結果をshowimg.htmlに転送する後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            host (str, optional): ホスト名。デフォルトは'localhost'。
            port (int, optional): ポート番号。デフォルトは6379。
            password (str, optional): パスワード。デフォルトは'password'。
            svname (str, optional): サーバ名。デフォルトは'server'。
            maxrecsize (int, optional): 最大レコードサイズ。デフォルトは1000。
        """
        super().__init__(logger)
        self.config = dict(host=host, port=port, password=password, svname=svname, maxrecsize=maxrecsize)
        self.injection = after_showimg_injection.AfterShowimgInjection(self.config, self.logger)

    def post(self, outputs:Dict[str, Any], output_image:Image.Image) -> Tuple[Dict[str, Any], Image.Image]:
        """
        後処理を行う関数です。

        Args:
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
            Image: 後処理結果
        """
        outputs, output_image = self.injection.action(None, None, outputs, output_image, None)
        return outputs, output_image
