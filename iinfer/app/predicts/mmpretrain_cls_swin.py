from iinfer.app import common, predict
from pathlib import Path
from PIL import Image
from typing import List, Tuple
import logging
import numpy as np

SITE = 'https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer'
IMAGE_WIDTH = 384
IMAGE_HEIGHT = 384
USE_MODEL_CONF = True

class MMPretrainClsSwin(predict.Predict):
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
        self.deploy_dir = model_path.parent
        import torch
        import mmpretrain
        device = torch.device('cuda' if torch.cuda.is_available() and gpu_id is not None else 'cpu')
        session = mmpretrain.ImageClassificationInferencer(str(model_conf_path), pretrained=str(model_path), device=device)
        return session

    def predict(self, session, img_width:int, img_height:int, image:Image, labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False):
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
        import mmpretrain
        # RGB画像をBGR画像に変換
        img_npy = common.img2npy(image)
        img_npy = common.bgr2rgb(img_npy)

        image_data, _, image_obj = self.preprocess_img(image, img_width, img_height)

        with open(self.deploy_dir / 'tmp.png', 'wb') as fp:
            fp.write(common.img2byte(image_obj,format='PNG'))
            result = session(self.deploy_dir / 'tmp.png')[0]

        output_scores = result["pred_scores"]
        output_classes = result["pred_class"]

        return dict(output_scores=output_scores, output_classes=output_classes), image_obj

    def resize_img(self, image:Image, to_w, to_h):
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
        image_data = np.expand_dims(image_data, 0)
        image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
        return image_data, image_size, image
