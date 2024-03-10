from iinfer.app import injection
from iinfer.app.postprocesses import csv
from PIL import Image
from typing import Tuple, Dict, Any
import logging


class AfterCSVInjection(injection.AfterInjection):
    """
    このクラスは推論実行後の後処理のインジェクションクラスです。
    """
    def __init__(self, config:Dict[str,Any], logger:logging.Logger):
        """
        このクラスのインスタンスを初期化します。
        継承時は、このコンストラクタを呼び出すようにしてください。
            super().__init__(logger)
        Args:
            config (Dict[str,Any]): 設定
            logger (logging.Logger): ロガー
        """
        super().__init__(config, logger)
        out_headers = self.get_config("out_headers", default=None)
        noheader = self.get_config("noheader", default=True)
        self.csv = csv.Csv(logger, out_headers=out_headers, noheader=noheader)
        self.csv_session = self.csv.create_session(None, None, None)

    def action(self, reskey:str, name:str, outputs:Dict[str, Any], output_image:Image.Image, session:Dict[str, Any]) -> Tuple[Dict[str, Any], Image.Image]:
        """
        このメソッドは推論を実行した後の処理を実行します。
        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            outputs (Dict[str, Any]): 推論結果。次の項目が含まれます。
                ・success or warn: 推論成功か警告のキーに対して、その内容が格納されます。
                ・output_image: 推論後の画像データをbase64エンコードした文字列
                ・output_image_shape: 推論後の画像データの形状（base46でコードするときに必要）
                ・output_image_name: クライアントから指定されてきた推論後の画像データの名前

            output_image (Image.Image): 推論後の画像データ
            session (Dict[str, Any]): 推論セッション。次の項目が含まれます。
                ・session: app.predict.Predict#create_session() で作成されたセッション
                ・model_img_width: モデルの入力画像の幅
                ・model_img_height: モデルの入力画像の高さ
                ・predict_obj: app.predict.Predict インスタンス
                ・labels: クラスラベルのリスト
                ・colors: ボックスの色のリスト
                ・tracker: use_trackがTrueの場合、トラッカーのインスタンス
        Returns:
            Tuple[Dict[str, Any], Image.Image]: 後処理後の推論結果と画像データのタプル
        """
        csv_str = self.csv.post_json(self.csv_session, outputs, output_image)
        self.add_success(outputs, csv_str)
        return outputs, output_image
