from iinfer.app import predict
from iinfer.app.commons import convert
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Union, Any
import logging
import numpy as np


SITE = 'https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4'
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = True

class OnnxClsEfficientNetLite4(predict.OnnxPredict):
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
        import onnxruntime as rt
        if self.is_gpu_available(model_path, model_conf_path, gpu_id):
            session = rt.InferenceSession(model_path, providers=[model_provider])
        else:
            session = rt.InferenceSession(model_path, providers=[model_provider], providers_options=[{'device_id': str(gpu_id)}])
        return session

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
        img_npy = convert.bgr2rgb(img_npy)

        image_data, _, image_obj = self.preprocess_img(input_data, img_width, img_height)

        results = model.run(["Softmax:0"], {"images:0": image_data})[0]

        output_scores, output_classes = [], []
        result = reversed(results[0].argsort()[-5:])
        for r in result:
            output_classes.append(r)
            output_scores.append(results[0][r])

        return dict(output_scores=output_scores, output_classes=output_classes), image_obj

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

    def preprocess_img(self, image:Image.Image, model_img_width:int, model_img_height:int):
        boxed_image = self.resize_img(image, model_img_width, model_img_height)
        image_data = np.array(boxed_image, dtype='float32')
        image_data /= 255.
        image_data = np.expand_dims(image_data, 0)
        image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
        return image_data, image_size, image
