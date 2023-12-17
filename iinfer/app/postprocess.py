from iinfer.app import common, client
from PIL import Image
from typing import Dict, Any
import logging
import json

class Postprocess(object):
    def __init__(self, logger:logging.Logger):
        """
        後処理クラスのベースクラスです。
        後処理クラスはこのクラスを継承してください。
        
        Args:
            logger (logging.Logger): ロガー
        """
        self.logger = logger

    def postprocess(self, json_sessionssion, img_sessionssion, res_str:str, timeout:int=60) -> Dict[str, Any]:
            """
            ポストプロセスを実行します。

            Args:
                json_sessionssion (任意): JSONセッション
                img_sessionssion (任意): 画像セッション
                res_str (str): 推論結果の文字列
                timeout (int, optional): タイムアウト時間（秒）。デフォルトは60。

            Returns:
                Dict[str, Any]: 処理結果(処理後の画像含む)
            """
            outputs = json.loads(res_str)
            output_image = None
            if "output_image" in outputs and "output_image_shape" in outputs:
                img_npy = common.b64str2npy(outputs["output_image"], outputs["output_image_shape"])
                output_image = common.npy2img(img_npy)
                del outputs["output_image"]
                del outputs["output_image_shape"]

            result = self.post_json(json_sessionssion, outputs)
            if type(result) == dict and output_image is not None:
                output_image = self.post_img(img_sessionssion, outputs, output_image)
                output_image_npy = common.img2npy(output_image)
                output_image_b64 = common.npy2b64str(output_image_npy)
                return dict(success=result, output_image=output_image_b64, output_image_shape=output_image_npy.shape)
            return dict(success=result)

    
    def create_session(self, json_connectstr:str, img_connectstr:str):
        """
        後処理のセッションを作成する関数です。
        ここで後処理準備を完了するようにしてください。
        戻り値の後処理セッションの型は問いません。

        Args:
            json_connectstr (str): 推論結果後処理のセッション確立に必要な接続文字列
            img_connectstr (str): 可視化画像後処理のセッション確立に必要な接続文字列

        Returns:
            推論結果後処理のセッション
            可視化画像後処理のセッション
        """
        raise NotImplementedError()

    def post_json(self, json_connectstr:str, outputs:Dict[str, Any]):
        """
        outputsに対して後処理を行う関数です。

        Args:
            json_connectstr (str): 推論結果の後処理に必要な接続文字列
            outputs (Dict[str, Any]): 推論結果

        Returns:
            Dict[str, Any]: 後処理結果
        """
        raise NotImplementedError()

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
        raise NotImplementedError()
