.. -*- coding: utf-8 -*-

****************************************************
カスタマイズ
****************************************************

カスタム推論モジュールについて
==============================

- AIモデルの配備 `iinfer -m client -c deploy <Option>` コマンドで `--predict_type Custom` 且つ `--custom_predict_py <カスタム推論pyファイル>` オプションを指定すると、カスタムモデルを配備できるようになります。
- カスタム推論pyファイルは `iinfer.app.predict.Predict` クラスを継承させたクラスを作成してください。
- `iinfer.app.predict.Predict` クラスの定義は下記の通りで、継承したクラスは `is_gpu_available` 、 `create_session` 、 `predict` メソッドを定義してください。
- なお、 `iinfer.app.predict.Predict` クラスを拡張した `iinfer.app.predict.OnnxPredict` 及び `iinfer.app.predict.TorchPredict` があり、 `is_gpu_available` メソッドが実装されています。

    .. code-block:: python3

            from pathlib import Path
            from PIL import Image
            from typing import List, Tuple, Dict, Any
            import logging

            class Predict(object):
                  def __init__(self, logger:logging.Logger) -> None:
                        """
                        このクラスのインスタンスを初期化します。
                        継承時は、このコンストラクタを呼び出すようにしてください。
                              super().__init__(logger)
                        Args:
                              logger (logging.Logger): ロガー
                        """
                        self.logger = logger

                  def is_gpu_available(self, gpu_id:int=None) -> bool:
                        """
                        GPUが利用可能かどうかを返す関数です。
                        戻り値がTrueの場合、GPUが利用可能です。
                        戻り値がFalseの場合、GPUが利用不可です。

                        Args:
                              gpu_id (int, optional): GPU ID. Defaults to None.
                        Returns:
                              bool: GPUが利用可能かどうか
                        """
                        raise NotImplementedError()

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

前処理、後処理モジュールについて
==================================

- AIモデルの配備 `iinfer -m client -c deploy <Option>` コマンドで `--before_injection_py <前処理pyファイル>` 及び `--after_injection_py <後処理pyファイル>` オプションを指定すると、サーバーサイドで実行する前処理及び後処理を配備できます。
- 前処理pyファイルは `iinfer.app.injection.BeforeInjection` クラスを継承させたクラスを作成してください。
- 後処理pyファイルは `iinfer.app.injection.AfterInjection` クラスを継承させたクラスを作成してください。
- `iinfer.app.injection.BeforeInjection` 及び `iinfer.app.injection.AfterInjection` クラスの定義は下記の通りで、継承したクラスは `action` メソッドを定義してください。
- `--before_injection_py <前処理pyファイル>` オプションを指定した場合、 `--before_injection_conf <前処理py用設定ファイル>` が指定できます。後処理も同様に指定できます。
- `--before_injection_conf <前処理py用設定ファイル>` を指定した場合、 `iinfer.app.injection.BeforeInjection` クラスのコンストラクタの `config` 引数にその設定値が渡されます。後処理も同様です。
- 前処理pyファイル及び後処理pyファイルのサンプルコードは、iinferのインストールパッケージ内の `extensions` フォルダ内にありますので参考にしてください。

    .. code-block:: python3

            class BeforeInjection(object):
                  """
                  このクラスは推論を実行する前処理のインジェクションクラスです。
                  """
                  def __init__(self, config:Dict[str,Any], logger:logging.Logger):
                        """
                        このクラスのインスタンスを初期化します。
                        継承時は、このコンストラクタを呼び出すようにしてください。
                              super().__init__(logger)
                        Args:
                              config (Dict[str,Any]): 設定
                              logger (logging.Logger): ロガー
                        """
                        self.config = config
                        self.logger = logger

                  def action(self, reskey:str, name:str, image:Image.Image, session:Dict[str, Any]) -> Image.Image:
                        """
                        このメソッドは推論を実行する前処理を実行します。
                        Args:
                              reskey (str): レスポンスキー
                              name (str): モデル名
                              image (Image.Image): 推論する画像データ
                              session (Dict[str, Any]): 推論セッション。次の項目が含まれます。
                                                      session: app.predict.Predict#create_session() で作成されたセッション
                                                      model_img_width: モデルの入力画像の幅
                                                      model_img_height: モデルの入力画像の高さ
                                                      predict_obj: app.predict.Predict インスタンス
                                                      labels: クラスラベルのリスト
                                                      colors: ボックスの色のリスト
                                                      tracker: use_trackがTrueの場合、トラッカーのインスタンス
                        Returns:
                              Image.Image: 前処理後の画像データ
                        """
                        return image

            class AfterInjection(object):
                  """
                  このクラスは推論実行後の後処理のインジェクションクラスです。
                  """
                  def __init__(self, config:Dict[str,Any], logger:logging.Logger):
                        """
                        このクラスのインスタンスを初期化します。
                        継承時は、このコンストラクタを呼び出すようにしてください。
                              super().__init__(logger)
                        Args:
                              config (Dict[str,Any]): 設定
                              logger (logging.Logger): ロガー
                        """
                        self.config = config
                        self.logger = logger

                  def action(self, reskey:str, name:str, outputs:Dict[str, Any], output_image:Image.Image, session:Dict[str, Any]) -> Tuple[Dict[str, Any], Image.Image]:
                        """
                        このメソッドは推論を実行した後の処理を実行します。
                        Args:
                              reskey (str): レスポンスキー
                              name (str): モデル名
                              outputs (Dict[str, Any]): 推論結果。次の項目が含まれます。
                                                      success or warn: 推論成功か警告のキーに対して、その内容が格納されます。
                                                      output_image: 推論後の画像データをbase64エンコードした文字列
                                                      output_image_shape: 推論後の画像データの形状（base46でコードするときに必要）
                                                      output_image_name: クライアントから指定されてきた推論後の画像データの名前
                              output_image (Image.Image): 推論後の画像データ
                              session (Dict[str, Any]): 推論セッション。次の項目が含まれます。
                                                      session: app.predict.Predict#create_session() で作成されたセッション
                                                      model_img_width: モデルの入力画像の幅
                                                      model_img_height: モデルの入力画像の高さ
                                                      predict_obj: app.predict.Predict インスタンス
                                                      labels: クラスラベルのリスト
                                                      colors: ボックスの色のリスト
                                                      tracker: use_trackがTrueの場合、トラッカーのインスタンス
                        Returns:
                              Tuple[Dict[str, Any], Image.Image]: 後処理後の推論結果と画像データのタプル
                        """
                        return outputs, output_image
