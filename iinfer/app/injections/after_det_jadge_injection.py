from iinfer.app import common, injection
from PIL import Image, ImageDraw
from typing import Tuple, Dict, Any


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
        nodraw = self.get_config('nodraw', False)

        try:
            outputs = self.post_json(outputs)
        except Exception as e:
            self.add_warning(outputs, str(e))
            return outputs, output_image

        try:
            if not nodraw:
                output_image = self.post_img(outputs, output_image)
        except Exception as e:
            self.add_warning(outputs, str(e))
            return outputs, output_image

        self.add_success(outputs, outputs['success']['output_jadge'])

        return outputs, output_image

    def post_json(self, outputs:Dict[str, Any]) -> Dict[str, Any]:
        """
        outputsに対して後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_ids': List[int],
                'output_scores': List[float],
                'output_classes': List[int],
                'output_labels': List[str],
                'output_boxes': List[List[int]],
                'output_tracks': List[int]
            }
        }
        Args:
            outputs (Dict[str, Any]): 推論結果
        Returns:
            Dict[str, Any]: 後処理後の推論結果
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

        if ok_score_th is not None and ((ok_classes is None or len(ok_classes)<=0) and (ok_labels is None or len(ok_labels)<=0)):
            raise Exception('If ok_score_th is specified, ok_classes or ok_labels must be set.')
        if ng_score_th is not None and ((ng_classes is None or len(ng_classes)<=0) and (ng_labels is None or len(ng_labels)<=0)):
            raise Exception('If ng_score_th is specified, ng_classes or ng_labels must be set.')
        if ext_score_th is not None and ((ext_classes is None or len(ext_classes)<=0) and (ext_labels is None or len(ext_labels)<=0)):
            raise Exception('If ext_score_th is specified, ext_classes or ext_labels must be set.')
        """
        if ok_score_th is not None and (not(ok_classes is not None and len(ok_classes)>0) or (ok_labels is not None and len(ok_labels)>0)):
            raise Exception('If ok_score_th is specified, ok_classes or ok_labels must be set.')
        if ng_score_th is not None and (not(ng_classes is not None and len(ng_classes)>0) or (ng_labels is not None and len(ng_labels)>0)):
            raise Exception(outputs, 'If ng_score_th is specified, ng_classes or ng_labels must be set.')
        if ext_score_th is not None and (not(ext_classes is not None and len(ext_classes)>0) or (ext_labels is not None and len(ext_labels)>0)):
            raise Exception(outputs, 'If ext_score_th is specified, ext_classes or ext_labels must be set.')
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_scores' not in data or 'output_classes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_scores\'] and outputs[\'success\'][\'output_classes\'] must be set.')

        output_jadge_score = [0.0, 0.0, 0.0] # ok, ng, ext
        for i, cls in enumerate(data['output_classes']):
            label = data['output_labels'][i] if 'output_labels' in data else None
            if ext_classes is not None and cls in ext_classes or ext_labels is not None and label in ext_labels:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])
            elif ng_classes is not None and cls in ng_classes or ng_labels is not None and label in ng_labels:
                output_jadge_score[1] = max(output_jadge_score[1], data['output_scores'][i])
            elif ok_classes is not None and cls in ok_classes or ok_labels is not None and label in ok_labels:
                output_jadge_score[0] = max(output_jadge_score[0], data['output_scores'][i])
            else:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])

        output_jadge_label = ['ok', 'ng', 'gray']
        output_jadge = 'gray'
        if ext_score_th is not None and output_jadge_score[2] >= ext_score_th:
            output_jadge = 'gray'
        elif ng_score_th is not None and output_jadge_score[1] >= ng_score_th:
            output_jadge = 'ng'
        elif ok_score_th is not None and output_jadge_score[0] >= ok_score_th:
            output_jadge = 'ok'

        data['output_jadge_score'] = output_jadge_score
        data['output_jadge_label'] = output_jadge_label
        data['output_jadge'] = output_jadge

        return outputs

    def post_img(self, outputs:Dict[str, Any], output_image:Image.Image) -> Image.Image:
        """
        output_imageに対して後処理を行う関数です。
        Args:
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 推論後の画像データ
        Returns:    
            Image: 後処理結果
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_jadge_score' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_jadge_score\'] must be set.')
        if 'output_jadge' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_jadge\'] must be set.')
        output_jadge_score = data['output_jadge_score']
        output_jadge = data['output_jadge']

        jadge_score = output_jadge_score[output_jadge_score.index(max(output_jadge_score))]
        draw = ImageDraw.Draw(output_image)

        color = common.make_color(str(jadge_score*1000))
        draw.rectangle(((0, 0), (output_image.width, 10)), outline=color, fill=color)
        draw.text((0, 0), f"{output_jadge}:{jadge_score}", tuple([int(255-c) for c in color]))

        return output_image
