from pathlib import Path
from PIL import Image
from iinfer.app import common, predict
from iinfer.app.commons import convert
from typing import List, Tuple
import json
import logging
import numpy as np
import shutil


SITE = 'https://github.com/deepinsight/insightface/tree/master/python-package'
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 640
REQUIREd_MODEL_CONF = False
REQUIREd_MODEL_WEIGHT = True

class InsightfaceDet(predict.OnnxPredict):
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
        from insightface.app import FaceAnalysis
        model_dir = model_path.parent / 'models'
        if not model_dir.exists():
            common.mkdirs(model_dir)
            shutil.unpack_archive(model_path, model_dir)
        fa = FaceAnalysis(name=model_path.stem, root=model_path.parent, providers=[model_provider])
        self.input_width = IMAGE_WIDTH
        self.input_height = IMAGE_HEIGHT
        fa.prepare(ctx_id=0, det_size=(self.input_height, self.input_width))
        face_store = []
        if model_conf_path is not None:
            with open(model_conf_path, 'r', encoding="utf-8") as f:
                for line in f:
                    outputs = json.loads(line)
                    if 'success' not in outputs or type(outputs['success']) != list:
                        raise Exception('Invalid model_conf. line[\'success\'] must be list.')
                    for data in outputs['success']:
                        if 'face_label' not in data:
                            raise Exception('Invalid outputs. line[\'success\'][i][\'face_label\'] must be set.')
                        if 'face_embedding' not in data:
                            raise Exception('Invalid outputs. line[\'success\'][i][\'face_embedding\'] must be set.')
                        if 'face_embedding_dtype' not in data:
                            raise Exception('Invalid outputs. line[\'success\'][i][\'face_embedding_dtype\'] must be set.')
                        if 'face_embedding_shape' not in data:
                            raise Exception('Invalid outputs. line[\'success\'][i][\'face_embedding_shape\'] must be set.')

                        face_store.append(dict(face_label=data['face_label'],
                                               face_embedding=convert.b64str2npy(data['face_embedding'], shape=data['face_embedding_shape'], dtype=data['face_embedding_dtype'])))

        return dict(fa=fa, face_store=face_store, face_threshold=0.0)

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
        if img_width != self.input_width or img_height != self.input_height:
            self.input_width = img_width
            self.input_height = img_height
            model['fa'].prepare(ctx_id=0, det_size=(self.input_height, self.input_width))

        # RGB画像をBGR画像に変換
        img_npy = convert.img2npy(image)
        img_npy = convert.bgr2rgb(img_npy)

        # 顔検知
        face_store = model['face_store']
        face_threshold = model['face_threshold']
        faces = model['fa'].get(img_npy)
        boxes = []
        scores = []
        clses = []
        labels = []
        ids = []
        embeddings = []
        embedding_dtypes = []
        embedding_shapes = []
        for i, face in enumerate(faces):
            box = face.bbox.astype(int)
            boxes.append([box[1], box[0], box[3], box[2]])
            embeddings.append(convert.npy2b64str(face.embedding))
            embedding_dtypes.append(face.embedding.dtype.name)
            embedding_shapes.append(face.embedding.shape)
            store_index, score = self.search_face(face_store, face.embedding, face_threshold)
            scores.append(score)
            ids.append(i)
            clses.append(0)
            if store_index >= 0:
                labels.append(face_store[store_index]['face_label'])
            else:
                labels.append(None)
        output_image, output_labels = common.draw_boxes(image, boxes, scores, clses, ids=ids, labels=labels, colors=colors, nodraw=nodraw)

        return dict(output_ids=ids, output_scores=scores, output_classes=clses, output_labels=output_labels, output_boxes=boxes,
                    output_embeddings=embeddings, output_embedding_dtypes=embedding_dtypes, output_embedding_shapes=embedding_shapes), output_image

    def search_face(self, store:list, face_embedding:np.array, th:float):
        last_score = -1
        index = -1
        for i,f in enumerate(store):
            score = self._compute_sim(f['face_embedding'], face_embedding)
            if score >= th and score > last_score:
                last_score = score
                index = i
        return index, last_score

    # REF: https://github.com/deepinsight/insightface/blob/f474870cc5b124749d482cf175818413a9fe12cd/python-package/insightface/model_zoo/arcface_onnx.py#L70
    def _compute_sim(self, feat1:np.array, feat2:np.array):
            """
            2つの特徴ベクトルのコサイン類似度を計算します。

            Parameters:
                feat1 (np.array): 特徴ベクトル1
                feat2 (np.array): 特徴ベクトル2

            Returns:
                float: 類似度の値
            """
            return np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2))
