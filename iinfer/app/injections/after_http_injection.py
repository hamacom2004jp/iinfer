from iinfer.app import common, injection
from PIL import Image
from typing import Tuple, Dict, Any
import datetime
import io
import requests

class AfterHttpInjection(injection.AfterInjection):

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
        outputs_url = self.get_config('outputs_url', None)
        if outputs_url is not None:
            resp = requests.post(outputs_url, json=outputs)
            if resp.status_code != 200:
                self.add_warning(outputs, f"HTTP POST request failed with status code {resp.status_code}. {outputs_url}")
            else:
                self.add_success(outputs, resp.text)
        else:
            self.add_warning(outputs, f"No outputs_url in config")

        output_image_url = self.get_config('output_image_url', None)
        if output_image_url is not None:
            ext = self.get_config('output_image_ext', 'jpeg')
            prefix = self.get_config('output_image_prefix', 'output_')
            img_bytes = common.img2byte(output_image, format=ext)
            finename = f'{prefix}{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}'
            finename = finename if 'output_image_name' not in outputs else outputs['output_image_name']
            file = {'file': (finename, io.BytesIO(img_bytes))}
            resp = requests.post(output_image_url, files=file)
            if resp.status_code != 200:
                self.add_warning(outputs, f"HTTP POST request failed with status code {resp.status_code}. {output_image_url}")
            else:
                self.add_success(outputs, resp.text)
        else:
            self.add_warning(outputs, "No output_image_url in config")

        return outputs, output_image
