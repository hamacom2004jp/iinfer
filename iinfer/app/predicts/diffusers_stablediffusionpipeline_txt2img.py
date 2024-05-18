from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple, Union, Any
import logging


SITE = 'https://huggingface.co/docs/diffusers/api/pipelines/stable_diffusion/text2img'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = False

class Diffusers_StableDiffusionPipeline_Txt2Img(predict.TorchPredict):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)

    def create_session(self, deploy_dir:Path, model_path:Union[Path|Any], model_conf_path:Path, model_provider:str, gpu_id:int=None):
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
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

        opt = common.loadopt(model_conf_path) if model_conf_path is not None else dict()
        self.num_inference_steps = common.getopt(opt, 'num_inference_steps', preval=10, withset=False)

        # KBlueLeaf/kohaku-v2.1
        # SimianLuo/LCM_Dreamshaper_v7
        pipeline = StableDiffusionPipeline.from_pretrained(model_path, cache_dir=deploy_dir)
        pipeline.scheduler = DPMSolverMultistepScheduler.from_config(pipeline.scheduler.config)
        if gpu_id is not None and self.is_gpu_available(model_path, model_conf_path, gpu_id):
            pipeline.to("cuda")
        return pipeline

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
        import torch
        output_images = model(input_data, height=img_height, width=img_width, num_inference_steps=self.num_inference_steps, output_type='pil',
                              torch_dtype=torch.float16).images

        return dict(prompt=input_data), output_images[0]
