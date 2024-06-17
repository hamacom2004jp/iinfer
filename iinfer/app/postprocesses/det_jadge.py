from iinfer.app import postprocess
from iinfer.app.commons import convert
from iinfer.app.injections import after_det_jadge_injection
from PIL import Image
from typing import Dict, Any, List
import cv2
import logging

class DetJadge(postprocess.Postprocess):
    def __init__(self, logger:logging.Logger,
                 ok_score_th:float=None, ok_classes:List[int]=None, ok_labels:List[str]=None,
                 ng_score_th:float=None, ng_classes:List[int]=None, ng_labels:List[str]=None,
                 ext_score_th:float=None, ext_classes:List[int]=None, ext_labels:List[str]=None,
                 nodraw:bool=False, output_preview:bool=False, json_without_img:bool=False):
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
            json_without_img (bool): JSONに画像を含めない場合はTrue。デフォルトはFalse。
        """
        super().__init__(logger, json_without_img)
        self.config = dict(ok_score_th=ok_score_th, ok_classes=ok_classes, ok_labels=ok_labels,
                           ng_score_th=ng_score_th, ng_classes=ng_classes, ng_labels=ng_labels,
                           ext_score_th=ext_score_th, ext_classes=ext_classes, ext_labels=ext_labels,
                           nodraw=nodraw, output_preview=output_preview)
        self.injection = after_det_jadge_injection.AfterDetJadgeInjection(self.config, self.logger)

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
        outputs = self.injection.post_json(outputs)
        data = outputs['success']
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
        output_image = self.injection.post_img(dict(success=result), output_image)
        output_preview = self.injection.get_config('output_preview', False)
        if output_preview:
            # RGB画像をBGR画像に変換
            img_npy = convert.img2npy(output_image).copy()
            img_npy = convert.bgr2rgb(img_npy)
            try:
                cv2.imshow('preview', img_npy)
                cv2.waitKey(1)
            except KeyboardInterrupt:
                pass
        return output_image
