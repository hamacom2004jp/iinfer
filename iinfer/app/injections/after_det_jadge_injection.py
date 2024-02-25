from iinfer.app import common, injection
from PIL import Image, ImageDraw
from typing import List, Tuple, Dict, Any
import datetime
import io
import requests

class AfterDetJadgeInjection(injection.AfterInjection):

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
        ok_score_th = self.get_config('ok_score_th', None)
        ok_classes = self.get_config('ok_classes', [])
        ok_labels = self.get_config('ok_labels', [])
        ng_score_th = self.get_config('ng_score_th', None)
        ng_classes = self.get_config('ng_classes', [])
        ng_labels = self.get_config('ng_labels', [])
        ext_score_th = self.get_config('ext_score_th', None)
        ext_classes = self.get_config('ext_classes', [])
        ext_labels = self.get_config('ext_labels', [])
        nodraw = self.get_config('nodraw', False)

        if ok_score_th is not None and ((ok_classes is not None and len(ok_classes)>0) or (ok_labels is not None and len(ok_labels)>0)):
            self.add_warning(outputs, 'If ok_score_th is specified, ok_classes or ok_labels must be set.')
            return outputs, output_image
        if ng_score_th is not None and ((ng_classes is not None and len(ng_classes)>0) or (ng_labels is not None and len(ng_labels)>0)):
            self.add_warning(outputs, 'If ng_score_th is specified, ng_classes or ng_labels must be set.')
            return outputs, output_image
        if ext_score_th is not None and ((ext_classes is not None and len(ext_classes)>0) or (ext_labels is not None and len(ext_labels)>0)):
            self.add_warning(outputs, 'If ext_score_th is specified, ext_classes or ext_labels must be set.')
            return outputs, output_image

        if 'success' not in outputs or type(outputs['success']) != dict:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'] must be dict.')
            return outputs, output_image
        data = outputs['success']
        if 'output_scores' not in data or 'output_classes' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_scores\'] and outputs[\'success\'][\'output_classes\'] must be set.')
            return outputs, output_image

        output_jadge_score = [0.0, 0.0, 0.0] # ok, ng, ext
        for i, cls in enumerate(data['output_classes']):
            label = data['output_labels'][i] if 'output_labels' in data else None
            if self.ext_classes is not None and cls in self.ext_classes or self.ext_labels is not None and label in self.ext_labels:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])
            elif self.ng_classes is not None and cls in self.ng_classes or self.ng_labels is not None and label in self.ng_labels:
                output_jadge_score[1] = max(output_jadge_score[1], data['output_scores'][i])
            elif self.ok_classes is not None and cls in self.ok_classes or self.ok_labels is not None and label in self.ok_labels:
                output_jadge_score[0] = max(output_jadge_score[0], data['output_scores'][i])
            else:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])

        output_jadge_label = ('ok', 'ng', 'gray')
        output_jadge = 'gray'
        if self.ext_score_th is not None and output_jadge_score[2] >= self.ext_score_th:
            output_jadge = 'gray'
        elif self.ng_score_th is not None and output_jadge_score[1] >= self.ng_score_th:
            output_jadge = 'ng'
        elif self.ok_score_th is not None and output_jadge_score[0] >= self.ok_score_th:
            output_jadge = 'ok'

        data['output_jadge_score'] = output_jadge_score
        data['output_jadge_label'] = output_jadge_label
        data['output_jadge'] = output_jadge

        jadge_score = output_jadge_score[output_jadge_score.index(max(output_jadge_score))]
        draw = ImageDraw.Draw(output_image)
        if not nodraw:
            color = common.make_color(str(jadge_score*1000))
            draw.rectangle(((0, 0), (output_image.width, 10)), outline=color, fill=color)
            draw.text((0, 0), f"{output_jadge}:{jadge_score}", tuple([int(255-c) for c in color]))

        return outputs, output_image
