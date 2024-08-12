from iinfer.app.injections import before_grayimg_injection
from typing import Dict, Any
import logging

class BeforeGrayimgInjection2(before_grayimg_injection.BeforeGrayimgInjection):
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
