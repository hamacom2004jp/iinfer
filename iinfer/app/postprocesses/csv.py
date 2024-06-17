from iinfer.app import postprocess
from iinfer.app.injections import after_csv_injection
from PIL import Image
from typing import Dict, List, Any
import logging

class Csv(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, out_headers:List[str]=None, noheader:bool=False, json_without_img:bool=False):
        """
        JSONをCSVに変換する後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            out_headers (List[str], optional): 出力させるヘッダー. Defaults to None.
            noheader (bool, optional): ヘッダーを出力しない. Defaults to False.
            json_without_img (bool, optional): JSONに画像を含めない場合はTrue. Defaults to False.
        """
        super().__init__(logger, json_without_img)
        self.config = dict(out_headers=out_headers, noheader=noheader)
        self.injection = after_csv_injection.AfterCSVInjection(self.config, self.logger)

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
        result = self.injection.write_csv(outputs, self.config['out_headers'], self.config['noheader'])
        self.config['noheader'] = True
        return result
