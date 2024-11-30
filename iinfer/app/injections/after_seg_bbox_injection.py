from cmdbox.app.commons import convert
from iinfer.app import injection
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
        try:
            outputs = self.post_json(outputs)
            self.add_success(outputs, "calc bboxes.")
        except Exception as e:
            self.add_warning(outputs, f'Error: {str(e)}')
        try:
            output_image = self.post_img(outputs, output_image)
            self.add_success(outputs, "draw bboxes.")
        except Exception as e:
            self.add_warning(outputs, f'Error: {str(e)}')

        return outputs, output_image


    def post_json(self, outputs:Dict[str, Any]) -> Dict[str, Any]:
        """
        outputsに対して後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_sem_seg': str,
                'output_sem_seg_shape': List[int],
                'output_sem_seg_dtype': str,
                'output_classes': List[int],
                'output_labels': List[str],
                'output_palette': List[int]
            }
        }
        Args:
            outputs (Dict[str, Any]): 推論結果
        Returns:
            Dict[str, Any]: 後処理結果
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        if 'output_sem_seg' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg\'] must be set.')
        if 'output_sem_seg_shape' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_shape\'] must be set.')
        if 'output_sem_seg_dtype' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_sem_seg_dtype\'] must be set.')
        if 'output_classes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_classes\'] must be set.')
        if 'output_labels' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_labels\'] must be set.')
        output_classes = data['output_classes']
        output_labels = data['output_labels']
        segment = convert.b64str2npy(data['output_sem_seg'], data['output_sem_seg_shape'], data['output_sem_seg_dtype'])
        output_boxes, output_rbboxes, output_rbboxes_rounds, output_boxes_classes, output_boxes_labels = self.gen_bboxes(segment[0,], output_classes, output_labels)
        del_segments = self.get_config('del_segments', True)
        data['output_boxes'] = output_boxes
        data['output_boxes_classes'] = output_boxes_classes
        data['output_boxes_labels'] = output_boxes_labels
        data['output_rbboxes'] = output_rbboxes
        data['output_rbboxes_rounds'] = output_rbboxes_rounds
        if del_segments:
            del data['output_sem_seg']
            del data['output_sem_seg_shape']
            del data['output_sem_seg_dtype']
        return outputs

    def post_img(self, outputs:Dict[str, Any], output_image:Image.Image) -> Image.Image:
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。
        Args:
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 入力画像（RGB配列であること）
        Returns:
            Image: 後処理結果
        """
        nodraw = self.get_config('nodraw', False)
        nodraw_bbox = self.get_config('nodraw_bbox', False)
        nodraw_rbbox = self.get_config('nodraw_rbbox', False)

        if not nodraw:
            if 'success' not in outputs or type(outputs['success']) != dict:
                raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
            data = outputs['success']
            if 'output_palette' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_palette\'] must be set.')
            if 'output_boxes' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_boxes\'] must be set.')
            if 'output_boxes_classes' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_boxes_classes\'] must be set.')
            if 'output_boxes_labels' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_boxes_labels\'] must be set.')
            if 'output_rbboxes' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_rbboxes\'] must be set.')
            if 'output_rbboxes_rounds' not in data:
                raise Exception('Invalid outputs. outputs[\'success\'][\'output_rbboxes_rounds\'] must be set.')
            output_palette = data['output_palette']
            output_boxes = data['output_boxes']
            output_boxes_classes = data['output_boxes_classes']
            output_boxes_labels = data['output_boxes_labels']
            output_rbboxes = data['output_rbboxes']
            output_rbboxes_rounds = data['output_rbboxes_rounds']

            draw = ImageDraw.Draw(output_image)
            if not nodraw_bbox:
                for box, cls, lbl in zip(output_boxes, output_boxes_classes, output_boxes_labels):
                    color = tuple(output_palette[cls])
                    draw.rectangle(box, outline=color)
                    draw.text((box[0], box[1]), lbl, fill=color)
            if not nodraw_rbbox:
                for rbox, cls, lbl, r in zip(output_rbboxes, output_boxes_classes, output_boxes_labels, output_rbboxes_rounds):
                    color = tuple(output_palette[cls])
                    draw.polygon([(p[0],p[1]) for p in rbox], outline=color, width=1)
                    draw.text((rbox[0][0], rbox[0][1]), f'{lbl}:{r:.2f}', fill=color)
        return output_image


    def gen_bboxes(self, mask, classes, labels):
        class_int = []
        label_str = []
        bbox_int = []
        rbbox_int = []
        rbbox_round = []
        mask_npy = mask.astype(np.uint8)
        for c, l in zip(classes, labels):
            seg = np.where(mask_npy == c, 255, 0).astype(np.uint8)
            contours, hierarchy = cv2.findContours(seg, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            for cont in contours:
                rect = cv2.minAreaRect(cont)
                box = cv2.boxPoints(rect)
                x_min = np.min(cont[:,:,0])
                x_max = np.max(cont[:,:,0])
                y_min = np.min(cont[:,:,1])
                y_max = np.max(cont[:,:,1])
                bbox_int.append([x_min.astype(int), y_min.astype(int), x_max.astype(int), y_max.astype(int)])
                rbbox_int.append(box.astype(np.int32).tolist())
                class_int.append(c)
                label_str.append(l)
                rbbox_round.append(rect[2])
        return bbox_int, rbbox_int, rbbox_round, class_int, label_str
