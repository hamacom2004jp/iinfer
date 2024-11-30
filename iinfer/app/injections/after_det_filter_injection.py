from cmdbox.app import common
from iinfer.app import injection
from PIL import Image
from typing import Tuple, Dict, Any


class AfterDetFilterInjection(injection.AfterInjection):

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

        self.add_success(outputs, "filterd")

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
            outputs (Dict[str, Any]): 推論結果。
        Returns:
            Dict[str, Any]: 後処理後の推論結果
        """
        score_th = self.get_config('score_th', 0.0)
        width_th = self.get_config('width_th', 0)
        height_th = self.get_config('height_th', 0)
        classes = self.get_config('classes', [])
        labels = self.get_config('labels', [])

        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_scores' not in data or 'output_classes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_scores\'] and outputs[\'success\'][\'output_classes\'] must be set.')
        output_ids = []
        output_scores = []
        output_classes = []
        output_labels = []
        output_boxes = []
        output_tracks = []
        for i, score in enumerate(data['output_scores']):
            if score < score_th:
                continue
            width = data['output_boxes'][i][2] - data['output_boxes'][i][0]
            height = data['output_boxes'][i][3] - data['output_boxes'][i][1]
            if width < width_th or height < height_th:
                continue
            if classes is not None and len(classes) > 0 and 'output_classes' in data:
                if data['output_classes'][i] not in classes:
                    continue
            if labels is not None and len(labels) > 0 and 'output_labels' in data:
                if data['output_labels'][i] not in labels:
                    continue
            output_ids.append(data['output_ids'][i])
            output_scores.append(score)
            output_classes.append(data['output_classes'][i])
            if 'output_labels' in data:
                output_labels.append(data['output_labels'][i])
            output_boxes.append(data['output_boxes'][i])
            if 'output_tracks' in data:
                output_tracks.append(data['output_tracks'][i])
        data['output_ids'] = output_ids
        data['output_scores'] = output_scores
        data['output_classes'] = output_classes
        if 'output_labels' in data:
            data['output_labels'] = output_labels
        data['output_boxes'] = output_boxes
        if 'output_tracks' in data:
            data['output_tracks'] = output_tracks

        return outputs

    def post_img(self, outputs:Dict[str, Any], output_image:Image.Image) -> Image.Image:
        """
        output_imageに対して後処理を行う関数です。
        Args:
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 推論後の画像データ
        Returns:
            Image.Image: 後処理後の画像データ
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception(outputs, 'Invalid outputs. outputs[\'success\'] must be dict.')

        nodraw = self.get_config('nodraw', False)

        data = outputs['success']
        output_ids = data["output_ids"] if "output_ids" in data else None
        output_labels = data["output_labels"] if "output_labels" in data else None
        output_tracks = data["output_tracks"] if "output_tracks" in data else output_ids
        image, output_labels = common.draw_boxes(output_image, data["output_boxes"], data["output_scores"], data["output_classes"],
                                                 ids=output_ids, labels=output_labels, tracks=output_tracks, nodraw=nodraw, nolookup=True)

        return image
