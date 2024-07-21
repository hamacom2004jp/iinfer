from iinfer.app import injection
from iinfer.app.commons import convert
from PIL import Image
from typing import Tuple, Dict, Any
import datetime
import io
import requests
import time

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
        #import http
        #http.client.HTTPConnection.debuglevel=1
        self.req_session = requests.Session()
        try:
            url = self.get_config('outputs_url', None)
            if url is not None:
                json_without_img = self.get_config('json_without_img', False)
                if json_without_img:
                    del outputs['output_image']
                    del outputs['output_image_shape']
                result = self.post_json(url, outputs)
                self.add_success(outputs, result)
        except Exception as e:
            self.add_warning(outputs, str(e))

        try:
            url = self.get_config('output_image_url', None)
            if url is not None:
                result = self.post_img(url, outputs, output_image)
                self.add_success(outputs, result)
        except Exception as e:
            self.add_warning(outputs, str(e))

        return outputs, output_image

    def post_json(self, url, outputs:Dict[str, Any]):
        tm = time.time()
        res = self.req_session.post(url, json=outputs, verify=False, timeout=30)
        if res.status_code != 200:
            raise Exception(f"HTTP POST request failed. status_code={res.status_code} res.reason={res.reason} res.text={res.text} url={url}")
        try:
            result = res.json()
        except:
            result = dict(success=res.text)
        return result

    def post_img(self, url, outputs:Dict[str, Any], output_image:Image.Image):
        finename = self.get_config('fileup_name', None)
        ext = self.get_config('output_image_ext', 'jpeg')
        if finename is None:
            prefix = self.get_config('output_image_prefix', 'output_')
            finename = f'{prefix}{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.{ext}'

        finename = finename if 'output_image_name' not in outputs else outputs['output_image_name']
        img_bytes = convert.img2byte(output_image, format=ext)
        file = {'file': (finename, io.BytesIO(img_bytes))}

        res = self.req_session.post(url, files=file, verify=False, timeout=30)
        if res.status_code != 200:
            raise Exception(f"HTTP POST request failed. status_code={res.status_code} res.reason={res.reason} res.text={res.text} url={url}")
        try:
            result = res.json()
        except:
            result = dict(success=res.text)
        return result
