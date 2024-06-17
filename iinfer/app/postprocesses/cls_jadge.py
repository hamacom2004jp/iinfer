from iinfer.app.postprocesses import det_jadge
from typing import List
import logging

class ClaJadge(det_jadge.DetJadge):
    def __init__(self, logger:logging.Logger,
                 ok_score_th:float=None, ok_classes:List[int]=None, ok_labels:List[str]=None,
                 ng_score_th:float=None, ng_classes:List[int]=None, ng_labels:List[str]=None,
                 ext_score_th:float=None, ext_classes:List[int]=None, ext_labels:List[str]=None,
                 nodraw:bool=False, output_preview:bool=False, json_without_img:bool=False):
        """
        Image Classification推論結果のクラススコア元に、この画像としてOK/NG/Grayの判定結果を追加する後処理クラスです。

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
        super().__init__(logger, ok_score_th=ok_score_th, ok_classes=ok_classes, ok_labels=ok_labels,
                         ng_score_th=ng_score_th, ng_classes=ng_classes, ng_labels=ng_labels,
                         ext_score_th=ext_score_th, ext_classes=ext_classes, ext_labels=ext_labels,
                         nodraw=nodraw, output_preview=output_preview, json_without_img=json_without_img)

