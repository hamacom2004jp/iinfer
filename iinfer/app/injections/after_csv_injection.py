from iinfer.app import injection
from PIL import Image
from typing import Tuple, Dict, Any
import csv
import io


class AfterCSVInjection(injection.AfterInjection):
    """
    このクラスは推論実行後の後処理のインジェクションクラスです。
    """

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
        out_headers = self.get_config("out_headers", default=None)
        noheader = self.get_config("noheader", default=True)
        result = self.write_csv(outputs, out_headers, noheader)
        self.add_success(outputs, result)
        return outputs, output_image
    
    def write_csv(self, outputs, out_headers, noheader):
        result = ''
        if 'success' in outputs and type(outputs['success']) == list:
            buffer = io.StringIO()
            for i, data in enumerate(outputs['success']):
                self._to_csv(data, buffer, i, out_headers, noheader)
            result = buffer.getvalue().strip()
            buffer.close()

        elif 'success' in outputs and type(outputs['success']) == dict:
            buffer = io.StringIO()
            self._to_csv(outputs['success'], buffer, 0, out_headers, noheader)
            result = buffer.getvalue().strip()
            buffer.close()

        elif type(outputs) == list:
            buffer = io.StringIO()
            for i, data in enumerate(outputs):
                self._to_csv(data, buffer, i, out_headers, noheader)
            result = buffer.getvalue().strip()
            buffer.close()

        elif type(outputs) == dict:
            buffer = io.StringIO()
            self._to_csv(outputs, buffer, 0, out_headers, noheader)
            result = buffer.getvalue().strip()
            buffer.close()

        else:
            buffer = io.StringIO()
            self._to_csv(outputs, buffer, 0, out_headers, noheader)
            result = buffer.getvalue().strip()
            buffer.close()
        
        return result

    def _to_csv(self, data, buffer, i, out_headers, noheader):
        if type(data) == dict:
            data_keys = data.keys()
            notfound = [] if out_headers is None else [h for h in out_headers if h not in data_keys]
            if len(notfound) > 0:
                raise Exception(f"notfound headers: {notfound}")
            headers = out_headers if out_headers is not None else list(data_keys)
            row = {k:v for k, v in data.items() if k in headers}
            w = csv.DictWriter(buffer, fieldnames=headers)
            if not noheader and i<=0:
                w.writeheader()
            w.writerow(row)
        elif type(data) == list:
            csv.writer(buffer).writerow(data)
        else:
            buffer.write(str(data))
            buffer.write("\n")
