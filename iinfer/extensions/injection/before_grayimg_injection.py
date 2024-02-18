from iinfer.app import injection
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Any
import logging

class BeforeGrayimgInjection(injection.BeforeInjection):
    """
    このクラスは推論を実行する前処理のインジェクションクラスです。
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

    def action(self, reskey:str, name:str, image:Image.Image, session:Dict[str, Any]) -> Image.Image:
        """
        このメソッドは推論を実行する前処理を実行します。
        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            image (Image.Image): 推論する画像データ
            session (Dict[str, Any]): 推論セッション。次の項目が含まれます。
                                      session: app.predict.Predict#create_session() で作成されたセッション
                                      model_img_width: モデルの入力画像の幅
                                      model_img_height: モデルの入力画像の高さ
                                      predict_obj: app.predict.Predict インスタンス
                                      labels: クラスラベルのリスト
                                      colors: ボックスの色のリスト
                                      tracker: use_trackがTrueの場合、トラッカーのインスタンス
        Returns:
            Image.Image: 前処理後の画像データ
        """
        return image.convert('L')
