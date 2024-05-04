from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple
import logging


SITE = 'https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/text2img'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = False

class Diffusers_StableDiffusion_Txt2Img(predict.TorchPredict):
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
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

        model_id = "KBlueLeaf/kohaku-v2.1"
        pipeline = StableDiffusionPipeline.from_pretrained(model_id, cache_dir=model_conf_path.parent)
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
        if gpu_id is not None:
            pipeline.to("cuda")
        return pipeline

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
        import torch
        prompt = "A Japanese woman is taking a shower while eating pizza."
        output_images = model(prompt, height=img_height, width=img_width, num_inference_steps=5, output_type='pil',
                              torch_dtype=torch.float16).images

        return dict(prompt=prompt), output_images[0]
