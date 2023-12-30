from iinfer.app import common, postprocess
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

    def post_json(self, json_connectstr,  outputs:Dict[str, Any]):
        """
        outputsに対して後処理を行う関数です。

        Args:
            json_connectstr (str): 使用しないパラメーター
            outputs (Dict[str, Any]): 推論結果

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

    def post_img(self, img_connectstr:str, outputs:Dict[str, Any], output_image:Image):
        """
        output_imageに対して後処理を行う関数です。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。

        Args:
            img_connectstr (str): 可視化画像の後処理に必要な接続文字列
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image): 入力画像（RGB配列であること）

        Returns:
            Image: 後処理結果
        """
        data = outputs['success']
        output_labels = data["output_labels"] if "output_labels" in data else None
        output_tracks = data["output_tracks"] if "output_tracks" in data else None
        image, output_labels = common.draw_boxes(output_image, data["output_boxes"], data["output_scores"], data["output_classes"],
                                                 ids=output_labels, labels=output_tracks, nodraw=self.nodraw, nolookup=True)
        if self.output_preview:
            # RGB画像をBGR画像に変換
            img_npy = common.img2npy(image)
            img_npy = common.bgr2rgb(img_npy)
            try:
                cv2.imshow('preview', img_npy)
                cv2.waitKey(1)
            except KeyboardInterrupt:
                pass
        return image
