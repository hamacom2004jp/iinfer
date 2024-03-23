from iinfer.app import injection
from iinfer.app.commons import convert
from PIL import Image, ImageDraw
from typing import Tuple, Dict, Any
import cv2
import numpy as np


class AfterSegBBoxInjection(injection.AfterInjection):

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
        nodraw_bbox = self.get_config('nodraw_bbox', False)
        nodraw_rbbox = self.get_config('nodraw_rbbox', False)

        if 'success' not in outputs or type(outputs['success']) != dict:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'] must be dict.')
            return outputs, output_image
        data = outputs['success']
        if 'output_sem_seg' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_sem_seg\'] must be set.')
            return outputs, output_image
        if 'output_sem_seg_shape' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_sem_seg_shape\'] must be set.')
            return outputs, output_image
        if 'output_sem_seg_dtype' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_sem_seg_dtype\'] must be set.')
            return outputs, output_image
        if 'output_classes' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_classes\'] must be set.')
            return outputs, output_image
        if 'output_labels' not in data:
            self.add_warning(outputs, 'Invalid outputs. outputs[\'success\'][\'output_labels\'] must be set.')
            return outputs, output_image

        output_classes = data['output_classes']
        output_labels = data['output_labels']
        segment = convert.b64str2npy(data['output_sem_seg'], data['output_sem_seg_shape'], data['output_sem_seg_dtype'])
        output_boxes, output_rbboxes, output_rounds = self.gen_bboxes(segment[0,], output_classes, output_labels)

        if not nodraw:
            draw = ImageDraw.Draw(output_image)
            if not nodraw_bbox:
                for box, lbl in zip(output_boxes, output_labels):
                    draw.rectangle(box, outline=(0,255,0))
                    draw.text((box[0], box[1]), lbl, fill=(0,255,0))
            if not nodraw_rbbox:
                for rbox, lbl, r in zip(output_rbboxes, output_labels, output_rounds):
                    draw.polygon([(p[0],p[1]) for p in rbox], outline=(0,255,255), width=1)
                    draw.text((rbox[0][0], rbox[0][1]), f'{lbl}:{r:.2f}', fill=(0,255,255))

        data['output_boxes'] = output_boxes
        data['output_rounds'] = output_rounds
        data['output_rbboxes'] = output_rbboxes

        self.add_success(outputs, "calc bboxes.")

        return outputs, output_image

    def gen_bboxes(self, mask, classes, labels):
        bbox_int = []
        rbbox_int = []
        rbbox_round = []
        mask_npy = mask.astype(np.uint8)
        for c, l in zip(classes, labels):
            seg = np.where(mask_npy == c, 255, 0).astype(np.uint8)
            contours, hierarchy = cv2.findContours(seg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                rect = cv2.minAreaRect(c)
                box = cv2.boxPoints(rect)
                x_min = np.min(c[:,:,0])
                x_max = np.max(c[:,:,0])
                y_min = np.min(c[:,:,1])
                y_max = np.max(c[:,:,1])
                bbox_int.append([x_min.astype(int), y_min.astype(int), x_max.astype(int), y_max.astype(int)])
                rbbox_int.append(box.astype(np.int32).tolist())
                rbbox_round.append(rect[2])
        return bbox_int, rbbox_int, rbbox_round
