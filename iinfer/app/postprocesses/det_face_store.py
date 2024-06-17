from iinfer.app.commons import convert
from iinfer.app.postprocesses import det_clip
from PIL import Image
from typing import Dict, Any
import logging
import numpy as np


class DetFaceStore(det_clip.DetClip):
    def __init__(self, logger:logging.Logger, face_threshold:float=0.0, image_type:str='capture', clip_margin:int=0, json_without_img:bool=False):
        """
        face Detectionの推論結果となったbbox部分を個別の画像として切り出す後処理クラスです。
        
        Args:
            logger (logging.Logger): ロガー
            face_threshold (float): 出力する顔スコアの閾値
            image_type (str): 切り出した画像のファイル形式
            clip_margin (int): bboxの周囲に余白を設けるピクセル数
            output_dir (Path): 切り出した画像を保存するディレクトリ
            json_without_img (bool, optional): JSONに画像を含めない場合はTrue。デフォルトはFalse。
        """
        super().__init__(logger, image_type, clip_margin, json_without_img)
        self.face_threshold = face_threshold

    def post_json(self, json_session, outputs:Dict[str, Any], output_image:Image.Image):
        """
        outputsに対して後処理を行う関数です。
        なおoutputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_boxes': List[List[int]],
                'output_embeddings': List[np.ndarray],
                'output_embedding_dtypes': List[str],
                'output_embedding_shapes': List[Tuple[int]],
                'output_scores': List[float],
                'output_image_name': str
            }
        }

        Args:
            json_session (任意): JSONセッション
            outputs (Dict[str, Any]): 推論結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Dict[str, Any]: 後処理結果
        """
        if 'success' not in outputs or type(outputs['success']) != dict:
            raise Exception('Invalid outputs. outputs[\'success\'] must be dict.')
        data = outputs['success']
        #if 'output_ids' not in data:
        #    raise Exception('Invalid outputs. outputs[\'success\'][\'output_ids\'] must be set.')
        #output_ids = data['output_ids']
        if 'output_boxes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_boxes\'] must be set.')
        output_boxes = data['output_boxes']
        if 'output_embeddings' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_embeddings\'] must be set.')
        output_embeddings = data['output_embeddings']
        if 'output_embedding_dtypes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_embedding_dtypes\'] must be set.')
        output_embedding_dtypes = data['output_embedding_dtypes']
        if 'output_embedding_shapes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_embedding_shapes\'] must be set.')
        output_embedding_shapes = data['output_embedding_shapes']
        if 'output_scores' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_scores\'] must be set.')
        output_scores = data['output_scores']
        
        # 切り出し
        result = []
        for i, box in enumerate(output_boxes):
            if output_scores[i] >= 0 and output_scores[i] <= self.face_threshold:
                continue
            y1, x1, y2, x2 = box
            x1 = max(0, np.floor(x1 + 0.5).astype(int) - self.clip_margin)
            y1 = max(0, np.floor(y1 + 0.5).astype(int) - self.clip_margin)
            x2 = min(output_image.width, np.floor(x2 + 0.5).astype(int) + self.clip_margin)
            y2 = min(output_image.height, np.floor(y2 + 0.5).astype(int) + self.clip_margin)

            cropped_image = output_image.crop((x1, y1, x2, y2))
            face_image_npy = convert.img2npy(cropped_image)

            img_b64 = None
            #face_name = f"{output_image_name}.{i}.{self.image_type}"
            if self.image_type == 'capture' or self.image_type is None:
                img_b64 = convert.npy2b64str(face_image_npy)
            else:
                img_byte = convert.img2byte(cropped_image, format=self.image_type)
                img_b64 = convert.bytes2b64str(img_byte)
            result.append(dict(face_label='', face_embedding=output_embeddings[i], face_embedding_dtype=output_embedding_dtypes[i], face_embedding_shape=output_embedding_shapes[i],
                               face_score=output_scores[i], face_box=[x1, y1, x2, y2], face_image_type=self.image_type, face_image_shape=face_image_npy.shape, face_image=img_b64))
            #result.append(dict(face_idx=output_ids[i], face_label='', face_name=face_name, face_scores=output_scores, face_image_type=self.image_type, face_image_shape=face_image_npy.shape, face_embedding=output_embeddings[i], face_image=img_b64))
        return result
    