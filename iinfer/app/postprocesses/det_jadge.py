from iinfer.app import common, postprocess
from PIL import Image, ImageDraw
from typing import Dict, Any, List
import cv2
import logging

class DetJadge(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger,
                 ok_score_th:float=None, ok_classes:List[int]=None, ok_labels:List[str]=None,
                 ng_score_th:float=None, ng_classes:List[int]=None, ng_labels:List[str]=None,
                 ext_score_th:float=None, ext_classes:List[int]=None, ext_labels:List[str]=None,
                 nodraw:bool=False, output_preview:bool=False):
        """
        Object Detection推論結果のクラススコア元に、この画像としてOK/NG/Grayの判定結果を追加する後処理クラスです。

        Args:
            logger (logging.Logger): ロガー
            ok_score_th (float): ok判定確定のスコアの閾値
            ok_classes (List[int]): ok判定確定のクラスのリスト
            ok_labels (List[str]): ok判定確定のラベルのリスト
            ng_score_th (float): ng判定確定のスコアの閾値
            ng_classes (List[int]): ng判定確定のクラスのリスト
            ng_labels (List[str]): ng判定確定のラベルのリスト
            ext_score_th (float): gray判定確定のスコアの閾値
            ext_classes (List[int]): gray判定確定のクラスのリスト
            ext_labels (List[str]): gray判定確定のラベルのリスト
            nodraw (bool): 描画しない
            output_preview (bool): プレビューを出力する
        """
        super().__init__(logger)
        if ok_score_th is not None and ((ok_classes is not None and len(ok_classes)>0) or (ok_labels is not None and len(ok_labels)>0)):
            raise Exception('If ok_score_th is specified, ok_classes or ok_labels must be set.')
        if ng_score_th is not None and ((ng_classes is not None and len(ng_classes)>0) or (ng_labels is not None and len(ng_labels)>0)):
            raise Exception('If ng_score_th is specified, ng_classes or ng_labels must be set.')
        if ext_score_th is not None and ((ext_classes is not None and len(ext_classes)>0) or (ext_labels is not None and len(ext_labels)>0)):
            self.add_warning(outputs, 'If ext_score_th is specified, ext_classes or ext_labels must be set.')
            raise Exception('If ext_score_th is specified, ext_classes or ext_labels must be set.')

        self.ok_score_th = ok_score_th
        self.ok_classes = ok_classes
        self.ok_labels = ok_labels
        self.ng_score_th = ng_score_th
        self.ng_classes = ng_classes
        self.ng_labels = ng_labels
        self.ext_score_th = ext_score_th
        self.ext_classes = ext_classes
        self.ext_labels = ext_labels
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

        output_jadge_score = [0.0, 0.0, 0.0] # ok, ng, ext
        for i, cls in enumerate(data['output_classes']):
            label = data['output_labels'][i] if 'output_labels' in data else None
            if self.ext_classes is not None and cls in self.ext_classes or self.ext_labels is not None and label in self.ext_labels:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])
            elif self.ng_classes is not None and cls in self.ng_classes or self.ng_labels is not None and label in self.ng_labels:
                output_jadge_score[1] = max(output_jadge_score[1], data['output_scores'][i])
            elif self.ok_classes is not None and cls in self.ok_classes or self.ok_labels is not None and label in self.ok_labels:
                output_jadge_score[0] = max(output_jadge_score[0], data['output_scores'][i])
            else:
                output_jadge_score[2] = max(output_jadge_score[2], data['output_scores'][i])

        output_jadge_label = ('ok', 'ng', 'gray')
        output_jadge = 'gray'
        if self.ext_score_th is not None and output_jadge_score[2] >= self.ext_score_th:
            output_jadge = 'gray'
        elif self.ng_score_th is not None and output_jadge_score[1] >= self.ng_score_th:
            output_jadge = 'ng'
        elif self.ok_score_th is not None and output_jadge_score[0] >= self.ok_score_th:
            output_jadge = 'ok'

        data['output_jadge_score'] = output_jadge_score
        data['output_jadge_label'] = output_jadge_label
        data['output_jadge'] = output_jadge

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
        output_jadge_score = data["output_jadge_score"] if "output_jadge_score" in data else 0.0
        output_jadge_label = data["output_jadge_label"] if "output_jadge_label" in data else None
        output_jadge = data["output_jadge"] if "output_jadge" in data else None
        jadge_score = output_jadge_score[output_jadge_score.index(max(output_jadge_score))]

        draw = ImageDraw.Draw(output_image)
        if not self.nodraw:
            color = common.make_color(str(jadge_score*1000))
            draw.rectangle(((0, 0), (output_image.width, 10)), outline=color, fill=color)
            draw.text((0, 0), f"{output_jadge}:{jadge_score}", tuple([int(255-c) for c in color]))

        image = output_image
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
