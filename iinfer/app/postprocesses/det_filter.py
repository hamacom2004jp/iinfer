from iinfer.app import common, postprocess
from iinfer.app.commons import convert
from PIL import Image
from typing import Dict, Any, List
import cv2
import logging

class DetFilter(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger, score_th:float=0.0, width_th:int=0, height_th:int=0, classes:List[int]=None, labels:List[str]=None, nodraw:bool=False, output_preview:bool=False):
        """
        Object Detectionの推論結果をフィルタリングする後処理クラスです。
        閾値に満たない推論結果を除外します。
        
        Args:
            logger (logging.Logger): ロガー
            score_th (float): スコアの閾値
            width_th (int): ボックスの幅の閾値
            height_th (int): ボックスの高さの閾値
            classes (List[int]): クラスのリスト
            labels (List[str]): ラベルのリスト
            nodraw (bool): 描画しない
            output_preview (bool): プレビューを出力する
        """
        super().__init__(logger)
        self.score_th = score_th
        self.width_th = width_th
        self.height_th = height_th
        self.classes = classes
        self.labels = labels
        self.nodraw = nodraw
        self.output_preview = output_preview

    def create_session(self, json_connectstr:str, img_connectstr:str, text_connectstr:str):
        """
        後処理のセッションを作成する関数です。
        ここで後処理準備を完了するようにしてください。
        戻り値の後処理セッションの型は問いません。

        Args:
            json_connectstr (str): 推論結果後処理のセッション確立に必要な接続文字列
            img_connectstr (str): 可視化画像後処理のセッション確立に必要な接続文字列
            text_connectstr (str): テキストデータ処理のセッション確立に必要な接続文字列

        Returns:
            推論結果後処理のセッション
            可視化画像後処理のセッション
            テキストデータ処理のセッション
        """
        return 'json_connectstr', 'img_connectstr', None

    def post_json(self, json_session, outputs:Dict[str, Any], output_image:Image.Image):
        """
        outputsに対して後処理を行う関数です。
        outputsは、以下のような構造を持つDict[str, Any]です。
        {
            'success': {
                'output_ids': List[int],
                'output_scores': List[float],
                'output_classes': List[int],
                'output_labels': List[str],
                'output_boxes': List[List[int]],
                'output_tracks': List[int]
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
        if 'output_scores' not in data or 'output_classes' not in data:
            raise Exception('Invalid outputs. outputs[\'success\'][\'output_scores\'] and outputs[\'success\'][\'output_classes\'] must be set.')
        output_boxes = []
        output_scores = []
        output_classes = []
        output_labels = []
        output_tracks = []
        for i, score in enumerate(data['output_scores']):
            if score < self.score_th:
                continue
            width = data['output_boxes'][i][2] - data['output_boxes'][i][0]
            height = data['output_boxes'][i][3] - data['output_boxes'][i][1]
            if width < self.width_th or height < self.height_th:
                continue
            if self.classes is not None and 'output_classes' in data:
                if data['output_classes'][i] not in self.classes:
                    continue
            if self.labels is not None and 'output_labels' in data:
                if data['output_labels'][i] not in self.labels:
                    continue
            output_boxes.append(data['output_boxes'][i])
            output_scores.append(score)
            output_classes.append(data['output_classes'][i])
            if 'output_labels' in data:
                output_labels.append(data['output_labels'][i])
            if 'output_tracks' in data:
                output_tracks.append(data['output_tracks'][i])
        data['output_boxes'] = output_boxes
        data['output_scores'] = output_scores
        data['output_classes'] = output_classes
        if 'output_labels' in data:
            data['output_labels'] = output_labels
        if 'output_tracks' in data:
            data['output_tracks'] = output_tracks
        return data

    def post_img(self, img_session, result:Dict[str, Any], output_image:Image.Image):
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。

        Args:
            img_session (任意): 画像セッション
            result (Dict[str, Any]): 後処理結果
            output_image (Image.Image): 入力画像（RGB配列であること）

        Returns:
            Image: 後処理結果
        """
        data = result
        output_labels = data["output_labels"] if "output_labels" in data else None
        output_tracks = data["output_tracks"] if "output_tracks" in data else None
        image, output_labels = common.draw_boxes(output_image, data["output_boxes"], data["output_scores"], data["output_classes"],
                                                 ids=output_labels, labels=output_tracks, nodraw=self.nodraw, nolookup=True)
        if self.output_preview:
            # RGB画像をBGR画像に変換
            img_npy = convert.img2npy(image)
            img_npy = convert.bgr2rgb(img_npy)
            try:
                cv2.imshow('preview', img_npy)
                cv2.waitKey(1)
            except KeyboardInterrupt:
                pass
        return image
