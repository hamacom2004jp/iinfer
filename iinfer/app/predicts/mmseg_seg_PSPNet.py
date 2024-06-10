from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple, Union, Any
import logging
import numpy as np


SITE = 'https://github.com/open-mmlab/mmsegmentation/tree/main/configs/pspnet'
IMAGE_WIDTH = 1024
IMAGE_HEIGHT = 512
REQUIREd_MODEL_CONF = True
REQUIREd_MODEL_WEIGHT = False

class MMSegPSPNet(predict.TorchPredict):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)

    def create_session(self, deploy_dir:Path, model_path:Union[Path,Any], model_conf_path:Path, model_provider:str, gpu_id:int=None):
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードを行い、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            deploy_dir (Path): デプロイディレクトリのパス
            model_path (Path|Any): モデルファイルのパス
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

    def predict(self, model, img_width:int, img_height:int, input_data:Union[Image.Image, str], labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False):
        """
        予測を行う関数です。
        predictコマンドやcaptureコマンド実行時に呼び出されます。
        引数のinput_dataが画像の場合RGBですので、戻り値の出力画像もRGBにしてください。
        戻り値の推論結果のdictは、通常推論結果項目ごとに値(list)を設定します。

        Args:
            model: 推論セッション
            img_width (int): モデルのINPUTサイズ（input_dataが画像の場合は、画像の幅）
            img_height (int): モデルのINPUTサイズ（input_dataが画像の場合は、画像の高さ）
            input_data (Image | str): 推論するデータ（画像の場合RGB配列であること）
            labels (List[str], optional): クラスラベルのリスト. Defaults to None.
            colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
        """
        # RGB画像をBGR画像に変換
        img_npy = convert.img2npy(input_data)

        from mmseg.apis import inference_model
        from mmseg.structures import SegDataSample

        result:SegDataSample = inference_model(model, img_npy)
        if hasattr(model, 'module'):
            model = model.module
        
        segment = result.pred_sem_seg.numpy()
        logits = result.seg_logits.numpy()
        output_catalog = model.dataset_meta['classes']
        output_palette = model.dataset_meta['palette']
        output_classes = np.unique(segment.data)
        output_labels = [output_catalog[i] for i in output_classes]
        output_sem_seg = convert.npy2b64str(segment.data)
        output_sem_seg_shape = segment.data.shape
        output_sem_seg_dtype = str(segment.data.dtype)
        output_seg_logits = convert.npy2b64str(logits.data)
        output_seg_logits_shape = logits.data.shape
        output_seg_logits_dtype = str(logits.data.dtype)

        if not nodraw:
            img = self.draw_mask(img_npy, result,
                                 labels if labels is not None else output_catalog,
                                 colors if colors is not None else model.dataset_meta['palette'])
            output_image = convert.npy2img(img)

        else:
            output_image = input_data

        return dict(output_catalog=output_catalog,
                    output_palette=output_palette,
                    output_classes=output_classes,
                    output_labels=output_labels,
                    output_sem_seg=output_sem_seg,
                    output_sem_seg_shape=output_sem_seg_shape,
                    output_sem_seg_dtype=output_sem_seg_dtype,
                    output_seg_logits=output_seg_logits,
                    output_seg_logits_shape=output_seg_logits_shape,
                    output_seg_logits_dtype=output_seg_logits_dtype), output_image

    def draw_mask(self, img_npy, result, classes, palette, alpha=0.5, with_labels=True):
        from mmseg.visualization import SegLocalVisualizer
        visualizer = SegLocalVisualizer(vis_backends=[dict(type='LocalVisBackend')], save_dir=None, alpha=alpha)
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
