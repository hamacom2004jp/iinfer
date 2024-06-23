from iinfer.app import postprocess
from iinfer.app.injections import after_http_injection
from PIL import Image
from typing import Dict, Tuple, Any
from urllib3.exceptions import InsecureRequestWarning
import logging
import requests
import urllib3
urllib3.disable_warnings(InsecureRequestWarning)

class Httpreq(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, fileup_name:str='file', outputs_url:str=None, output_image_url:str=None,
                 output_image_ext:str='jpeg', output_image_prefix:str='output_', json_without_img:bool=False):
        """
        HTTP Requestを行う後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            fileup_name (str, optional): ファイルアップロード名。デフォルトは'file'。
            json_url (str, optional): JSONの送信先URL。デフォルトはNone。
            img_url (str, optional): 画像の送信先URL。デフォルトはNone。
            text_url (str, optional): テキストの送信先URL。デフォルトはNone。
            output_image_ext (str, optional): 画像の拡張子。デフォルトは'jpeg'。
            output_image_prefix (str, optional): 画像のファイル名の接頭辞。デフォルトは'output_'。
            json_without_img (bool, optional): JSONに画像を含めない場合はTrue。デフォルトはFalse。
        """
        super().__init__(logger)
        self.fileup_name = fileup_name
        self.config = dict(fileup_name=fileup_name, outputs_url=outputs_url, output_image_url=output_image_url,
                           output_image_ext=output_image_ext, output_image_prefix=output_image_prefix, json_without_img=json_without_img)
        self.injection = after_http_injection.AfterHttpInjection(self.config, self.logger)
        self.injection.req_session = requests.Session()

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
