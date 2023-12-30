from pathlib import Path
from PIL import Image
from typing import List, Tuple
from iinfer.app import common, predict
from iinfer.app.predicts import onnx_det_YoloV3
import logging
import numpy as np


SITE = 'https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3'
IMAGE_WIDTH = 416
IMAGE_HEIGHT = 416
USE_MODEL_CONF = False

class OnnxDetTinyYoloV3(predict.Predict):
    def create_session(self, logger:logging.Logger, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None):
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードを行い、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            logger (logging.Logger): ロガー
            model_path (Path): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            推論セッション
        """
        return onnx_det_YoloV3.create_session(model_path, model_conf_path, model_provider, gpu_id)

    def predict(self, session, img_width:int, img_height:int, image:Image.Image, labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False):
        """
        予測を行う関数です。
        predictコマンドやcaptureコマンド実行時に呼び出されます。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。
        戻り値の推論結果のdictは、通常推論結果項目ごとに値(list)を設定します。
        例）Image Classification（EfficientNet_Lite4）の場合
        return dict(output_scores=output_scores, output_classes=output_classes), image_obj
        例）Object Detection（YoloX）の場合
        return dict(output_boxes=final_boxes, output_scores=final_scores, output_classes=final_cls_inds), output_image

        Args:
            session: 推論セッション
            img_width (int): モデルのINPUTサイズ（画像の幅）
            img_height (int): モデルのINPUTサイズ（画像の高さ）
            image (Image): 入力画像（RGB配列であること）
            labels (List[str], optional): クラスラベルのリスト. Defaults to None.
            colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
        """
        image_data, image_size, image_obj = self.preprocess_img(image, img_width, img_height)

        input_name = session.get_inputs()[0].name           # 'image'
        input_name_img_shape = session.get_inputs()[1].name # 'image_shape'
        output_name_boxes = session.get_outputs()[0].name   # 'boxes'
        output_name_scores = session.get_outputs()[1].name  # 'scores'
        output_name_indices = session.get_outputs()[2].name # 'indices'

        outputs_index = session.run([output_name_boxes, output_name_scores, output_name_indices],
                                    {input_name: image_data, input_name_img_shape: image_size})

        output_boxes = outputs_index[0]
        output_scores = outputs_index[1]
        output_indices = outputs_index[2]

        out_boxes, out_scores, out_classes = [], [], []
        for idx_ in output_indices[0]:
            out_classes.append(idx_[1])
            out_scores.append(output_scores[tuple(idx_)])
            idx_1 = (idx_[0], idx_[2])
            out_boxes.append(output_boxes[idx_1])

        output_image, output_labels = common.draw_boxes(image_obj, out_boxes, out_scores, out_classes, labels=labels, colors=colors, nodraw=nodraw)

        return dict(output_boxes=out_boxes, output_scores=out_scores, output_classes=out_classes, output_labels=output_labels), output_image

    def resize_img(self, image:Image.Image, to_w, to_h):
        '''resize image with unchanged aspect ratio using padding'''
        iw, ih = image.size
        scale = min(to_w/iw, to_h/ih)
        nw = int(iw*scale)
        nh = int(ih*scale)
        image = image.resize((nw,nh), Image.BICUBIC)
        new_image = Image.new('RGB', (to_w, to_h), (128,128,128))
        new_image.paste(image, ((to_w-nw)//2, (to_h-nh)//2))
        return new_image

    def preprocess_img(self, image:Image, model_img_width:int, model_img_height:int):
        boxed_image = self.resize_img(image, model_img_width, model_img_height)
        image_data = np.array(boxed_image, dtype='float32')
        image_data /= 255.
        image_data = np.transpose(image_data, [2, 0, 1])
        image_data = np.expand_dims(image_data, 0)
        image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
        return image_data, image_size, image
