from iinfer.app import postprocess
from PIL import Image
from typing import Dict, List, Any
import csv
import io
import logging

class Csv(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, out_headers:List[str]=None, noheader:bool=False):
        """
        JSONをCSVに変換する後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            out_headers (List[str], optional): 出力させるヘッダー. Defaults to None.
            noheader (bool, optional): ヘッダーを出力しない. Defaults to False.
        """
        super().__init__(logger)
        self.out_headers = out_headers
        self.noheader = noheader

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
        def _to_csv(data, buffer, i):
            if type(data) == dict:
                data_keys = data.keys()
                notfound = [] if self.out_headers is None else [h for h in self.out_headers if h not in data_keys]
                if len(notfound) > 0:
                    raise Exception(f"notfound headers: {notfound}")
                headers = self.out_headers if self.out_headers is not None else list(data_keys)
                row = {k:v for k, v in data.items() if k in headers}
                w = csv.DictWriter(buffer, fieldnames=headers)
                if not self.noheader and i<=0:
                    w.writeheader()
                w.writerow(row)
            elif type(data) == list:
                csv.writer(buffer).writerow(data)
            else:
                buffer.write(str(data))
                buffer.write("\n")

        result = ''
        if 'success' in outputs and type(outputs['success']) == list:
            buffer = io.StringIO()
            for i, data in enumerate(outputs['success']):
                _to_csv(data, buffer, i)
            result = buffer.getvalue().strip()
            buffer.close()

        elif 'success' in outputs and type(outputs['success']) == dict:
            buffer = io.StringIO()
            _to_csv(outputs['success'], buffer, 0)
            result = buffer.getvalue().strip()
            buffer.close()

        elif type(outputs) == list:
            buffer = io.StringIO()
            for i, data in enumerate(outputs):
                _to_csv(data, buffer, i)
            result = buffer.getvalue().strip()
            buffer.close()

        elif type(outputs) == dict:
            buffer = io.StringIO()
            _to_csv(outputs, buffer, 0)
            result = buffer.getvalue().strip()
            buffer.close()

        else:
            buffer = io.StringIO()
            _to_csv(outputs, buffer, 0)
            result = buffer.getvalue().strip()
            buffer.close()

        self.noheader = True
        return result
