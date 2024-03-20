from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple
import cv2
import logging
import numpy as np


SITE = 'https://github.com/open-mmlab/mmsegmentation/tree/main/configs/pspnet'
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 512
USE_MODEL_CONF = True

class MMSegPSPNet(predict.TorchPredict):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)

    def create_session(self, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None):
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードを行い、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            model_path (Path): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            推論セッション
        """
        from mmseg.apis import init_model
        import torch
        gpu = f'cuda:{gpu_id}' if gpu_id is not None else 'cuda'
        device = torch.device(gpu if self.is_gpu_available(model_path, model_conf_path, gpu_id) else 'cpu')
        model = init_model(model_conf_path, str(model_path), device=device) # , cfg_options = {'show': True}
        return model

    def predict(self, model, img_width:int, img_height:int, image:Image.Image, labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False):
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
            model: 推論セッション
            img_width (int): モデルのINPUTサイズ（画像の幅）
            img_height (int): モデルのINPUTサイズ（画像の高さ）
            image (Image): 入力画像（RGB配列であること）
            labels (List[str], optional): クラスラベルのリスト. Defaults to None.
            colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
        """
        # RGB画像をBGR画像に変換
        img_npy = convert.img2npy(image)

        from mmseg.apis import inference_model
        from mmseg.structures import SegDataSample

        result:SegDataSample = inference_model(model, img_npy)
        if hasattr(model, 'module'):
            model = model.module
        
        segment = result.pred_sem_seg.numpy()
        output_labels = model.dataset_meta['classes']
        output_classes = [i for i in range(len(output_labels))]
        output_sem_seg = convert.npy2b64str(segment.data)
        output_seg_logits = convert.npy2b64str(result.seg_logits.numpy().data)
        output_bbox, contours = self.gen_bboxes(segment.data[0,], output_classes)

        if not nodraw:
            img = self.draw_mask(img_npy, result,
                                 labels if labels is not None else output_labels,
                                 colors if colors is not None else model.dataset_meta['palette'])
            img = cv2.drawContours(img, [c.astype(np.int32) for c in contours], -1, (0,255,0), 1)
            output_image = convert.npy2img(img)

        else:
            output_image = image

        return dict(output_classes=output_classes,
                    output_labels=output_labels,
                    output_bbox=output_bbox,
                    output_sem_seg=output_sem_seg,
                    output_seg_logits=output_seg_logits), output_image

        return dict(output_ids=ids, output_scores=scores, output_classes=clses, output_labels=output_labels, output_boxes=boxes), output_image

    def draw_mask(self, img_npy, result, classes, palette, alpha=0.5, with_labels=True):
        from mmseg.visualization import SegLocalVisualizer
        visualizer = SegLocalVisualizer(vis_backends=[dict(type='LocalVisBackend')], alpha=alpha)
        visualizer.dataset_meta = dict(classes=classes, palette=palette)
        visualizer.add_datasample(
            name='input',
            image=img_npy,
            data_sample=result,
            draw_gt=False,
            draw_pred=True,
            show=False,
            with_labels=with_labels)
        img = visualizer.get_image()
        return img

    def gen_bboxes(self, mask, classes):
        ret = []
        output_bbox = []
        mask_npy = mask.astype(np.uint8)
        for i in range(1, len(classes)):
            m = np.where(mask_npy == i, 255, 0).astype(np.uint8)
            contours, hierarchy = cv2.findContours(m, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) < 1:
                continue
            rect = cv2.minAreaRect(contours[0])
            box = cv2.boxPoints(rect)
            output_bbox.append(box.astype(np.int32).tolist())
            ret.append(box)
        return output_bbox, ret
