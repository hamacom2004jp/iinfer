from iinfer.app import postprocess
from iinfer.app.injections import after_cmd_injection
from PIL import Image
from typing import Dict, Tuple, Any
import logging


class Cmd(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger,
                 cmdline:str='cwd', output_image_ext:str='jpeg', output_maxsize:int=1024*1024*5):
        """
        推論結果を環境変数にセットして任意のコマンドを実行する後処理クラスです。

        Args:
            logger (logging.Logger): ロガー
            cmdline (List[str], optional): コマンドライン。デフォルトは'cwd'。
            output_image_ext (str, optional): 出力画像のフォーマット。デフォルトは'jpeg'。
            output_maxsize (int, optional): 出力画像の最大サイズ。デフォルトは1024*1024*5。
        """
        super().__init__(logger)
        self.config = dict(cmdline=cmdline, output_image_ext=output_image_ext, output_maxsize=output_maxsize)
        self.injection = after_cmd_injection.AfterCmdInjection(self.config, self.logger)

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
