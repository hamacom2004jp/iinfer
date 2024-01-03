.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（clientモード）
****************************************************

clientモードのコマンド一覧です。

クライアント(AIモデルの配備) : `iinfer -m client -c deploy <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名(任意)を指定する"
    "--model_file <モデルファイル>","〇","学習済みのモデルファイルを指定する"
    "--model_conf_file <モデル設定ファイル>","","mmlabの場合はモデル設定ファイルを指定する。複数指定可能ですが、最初に指定したファイルが `start` 時に使用されます。"
    "--model_img_width <モデルのINPUTサイズ(横px)>","","AIモデルのINPUTサイズ(横px)を指定する"
    "--model_img_height <モデルのINPUTサイズ(縦px)>","","AIモデルのINPUTサイズ(縦px)を指定する"
    "--predict_type <推論タイプ>","〇","AIモデルの推論タイプを指定する。 :ref:`参照<predict_type_list>` "
    "--custom_predict_py <カスタム推論pyファイル>","","独自の推論タイプを作成するときに指定。この時は `--predict_type Custom` を指定"
    "--label_file <ラベルファイル>","","推論結果のクラスラベルファイルを指定。改行区切りでラベル名(行indexがクラスと一致する)を指定したファイル。"
    "--color_file <色ファイル>","","推論結果の可視化画像の色ファイルを指定。改行区切りで色(行indexがクラスと一致する)を指定したファイル。"
    "--overwrite","","デプロイ済みであっても上書きする"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

クライアント(AIモデルの配備一覧) : `iinfer -m client -c deploy_list <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

クライアント(AIモデルの配備解除) : `iinfer -m client -c undeploy <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定する"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

クライアント(AIモデルの起動) : `iinfer -m client -c start <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定する"
    "--model_provider <モデルプロバイダー>","","ONNX形式のモデルファイルの場合に指定可能。指定可能なプロバイダーは `CPUExecutionProvider` , `CUDAExecutionProvider` , `TensorrtExecutionProvider` "
    "--use_track","","ObjectDetectionタスクの場合に指定可能。motpyを使ってトラッキングID付与を行う"
    "--gpuid <GPUのid>","","GPUのディバイスIDを指定する。 `--model_provider` でGPUを使用するプロバイダーを指定した時に使用可能"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

.. _predict_type_list:

クライアント(推論タイプ一覧) : `iinfer -m client -c predict_type_list <Option>`
================================================================================

推論タイプ一覧を出力します。オプションの指定はありません。

クライアント(AIモデルの停止) : `iinfer -m client -c stop <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定する"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

クライアント(推論の実行) : `iinfer -m client -c predict <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定する"
    "-i,--input_file <推論対象の画像ファイル>","","推論させる画像をファイルで指定する"
    "--stdin","","推論させる画像を標準入力から読み込む"
    "--nodraw","","推論結果画像にbbox等の描き込みを行わない"
    "--image_type <推論対象の画像タイプ>","","推論させる画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "-o,--output_file <推論結果画像の保存先ファイル>","--stdinを指定した時〇","推論結果画像の保存先ファイルを指定する"
    "-P,--output_preview","","推論結果画像を `cv2.imshow` で表示する"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

クライアント(キャプチャーの実行) : `iinfer -m client -c capture <Option>`
==============================================================================

このコマンドは、パイプで接続して下記のように使用します。

.. code-block:: bat

   iinfer -m client -c capture <Option> | iinfer -m client -c predict --stdin --image_type capture <Option>

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--capture_device <ディバイス>","","キャプチャーディバイスを指定する。 `cv2.VideoCapture` の第一引数に渡される値。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--capture_frame_width <キャプチャーサイズ(横px)>","","キャプチャーする画像の横px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_WIDTH` オプションに指定する値。"
    "--capture_frame_height <キャプチャーサイズ(縦px)>","","キャプチャーする画像の縦px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_HEIGHT` オプションに指定する値。"
    "--capture_fps <キャプチャーFPS>","","キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepする"
    "--capture_count <キャプチャー回数>","","キャプチャー回数。AIの推論速度が指定した値より高速な場合に残り時間分をsleepする"
    "--output_preview","","推論結果画像を `cv2.imshow` で表示する"
