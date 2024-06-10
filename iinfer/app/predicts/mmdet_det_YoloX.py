from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple, Union, Any
import logging


SITE = 'https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = True
REQUIREd_MODEL_WEIGHT = False

class MMDetYoloX(predict.TorchPredict):
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
        from mmdet.apis import init_detector
        import torch
        gpu = f'cuda:{gpu_id}' if gpu_id is not None else 'cuda'
        device = torch.device(gpu if self.is_gpu_available(model_path, model_conf_path, gpu_id) else 'cpu')
        model = init_detector(model_conf_path, str(model_path), device=device) # , cfg_options = {'show': True}
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
        img_npy = convert.bgr2rgb(img_npy)

        #input_shape = (img_width, img_height)
        #img, ratio = self.preprocess(img_npy, input_shape)

        #output = session.run(None, {session.get_inputs()[0].name: img[None, :, :, :]})
        from mmdet.apis import inference_detector
        result = inference_detector(model, img_npy)
        boxes = result.pred_instances.bboxes.cpu().numpy().tolist()
        boxes = [[row[1],row[0],row[3],row[2]] for row in boxes]
        ids = [i for i in range(len(boxes))]
        scores = result.pred_instances.scores.cpu().numpy().tolist()
        clses = result.pred_instances.labels.cpu().numpy().tolist()
        output_image, output_labels = common.draw_boxes(input_data, boxes, scores, clses, ids=ids, labels=labels, colors=colors, nodraw=nodraw)
        return dict(output_ids=ids, output_scores=scores, output_classes=clses, output_labels=output_labels, output_boxes=boxes), output_image
