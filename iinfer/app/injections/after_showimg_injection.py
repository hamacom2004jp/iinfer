from cmdbox.app import options
from cmdbox.app.commons import convert, redis_client
from iinfer.app import injection
from PIL import Image
from typing import Tuple, Dict, Any
import logging

class AfterShowimgInjection(injection.AfterInjection):
    def __init__(self, config:Dict[str,Any], logger:logging.Logger):
        super().__init__(config, logger)
        opts = options.Options.getInstance()
        self.default_host = opts.get_cmd_opt('server', 'start', 'host')['default']
        self.default_port = opts.get_cmd_opt('server', 'start', 'port')['default']
        self.default_password = opts.get_cmd_opt('server', 'start', 'password')['default']
        self.default_svname = opts.get_cmd_opt('server', 'start', 'svname')['default']

        host = self.get_config('host', self.default_host)
        port = self.get_config('port', self.default_port)
        password = self.get_config('password', self.default_password)
        svname = self.get_config('svname', self.default_svname)
        self.redis_cli = redis_client.RedisClient(self.logger, host=host, port=port, password=password, svname=svname)

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
        maxrecsize = self.get_config('maxrecsize', 200)

        try:
            img_npy = convert.img2npy(output_image)
            outputs['output_image'] = convert.npy2b64str(img_npy)
            outputs['output_image_shape'] = img_npy.shape
            result = self.redis_cli.send_showimg('outputs', outputs, maxrecsize=maxrecsize)
            self.add_success(outputs, result)
            del outputs['output_image']
            del outputs['output_image_shape']
        except Exception as e:
            self.add_warning(outputs, str(e))

        return outputs, output_image
