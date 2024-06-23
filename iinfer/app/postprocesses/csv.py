from iinfer.app import postprocess
from iinfer.app.injections import after_csv_injection
from PIL import Image
from typing import Dict, List, Tuple, Any
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
        self.config = dict(out_headers=out_headers, noheader=noheader)
        self.injection = after_csv_injection.AfterCSVInjection(self.config, self.logger)

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
        result = self.injection.write_csv(outputs, self.config['out_headers'], self.config['noheader'])
        self.config['noheader'] = True
        return result, output_image
