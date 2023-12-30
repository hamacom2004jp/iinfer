.. -*- coding: utf-8 -*-

****************************************************
カスタマイズ
****************************************************

カスタム推論モジュールについて
==============================

- AIモデルの配備 `iinfer -m client -c deploy <Option>` コマンドで `--predict_type Custom` 且つ `--custom_predict_py <カスタム推論pyファイル>` オプションを指定すると、カスタムモデルを配備できるようになります。
- カスタム推論pyファイルは `iinfer.app.predict.Predict` クラスを継承させたクラスを作成してください。
- `iinfer.app.predict.Predict` クラスの定義は下記の通りで、継承したクラスは `create_session` と `predict` メソッドを定義してください。

    .. code-block:: python3

         from pathlib import Path
         from PIL import Image
         from typing import List, Tuple, Dict, Any
         import logging

         class Predict(object):
            def create_session(self, logger:logging.Logger, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None) -> Any:
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
               raise NotImplementedError()

            def predict(self, session, img_width:int, img_height:int, image:Image.Image, labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False) -> Tuple[Dict[str, Any], Image.Image]:
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
               raise NotImplementedError()
