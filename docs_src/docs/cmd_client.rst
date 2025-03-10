.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（clientモード）
****************************************************

clientモードのコマンド一覧です。

クライアント(キャプチャーの実行) : `iinfer -m client -c capture <Option>`
==============================================================================

このコマンドは、パイプで接続して下記のように使用します。

.. code-block:: bat

   iinfer -m client -c capture <Option> | iinfer -m client -c predict --stdin --pred_image_type capture <Option>

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--capture_device <ディバイス>","","キャプチャーディバイスを指定します。 `cv2.VideoCapture` の第一引数に渡される値。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--capture_frame_width <キャプチャーサイズ(横px)>","","キャプチャーする画像の横px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_WIDTH` オプションに指定する値。"
    "--capture_frame_height <キャプチャーサイズ(縦px)>","","キャプチャーする画像の縦px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_HEIGHT` オプションに指定する値。"
    "--capture_fps <キャプチャーFPS>","","キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepします"
    "--capture_count <キャプチャー回数>","","キャプチャーする回数。"
    "--output_preview","","推論結果画像を `cv2.imshow` で表示します"
    "--output_csv <処理結果csvの保存先ファイル>","","キャプチャーした内容をcsvで保存します。これを指定した場合、標準出力は行いません。"
    "-o, --output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, --output_json_append","","このオプションは使用できません"


クライアント(AIモデルの配備一覧) : `iinfer -m client -c deploy_list <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間を指定"


クライアント(AIモデルの配備) : `iinfer -m client -c deploy <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "--model_file <モデルファイル>","〇","学習済みのモデルファイルのパス又はダウンロードURLを指定します"
    "--model_conf_file <モデル設定ファイル>","","モデル設定ファイルを指定します。複数指定可能ですが、最初に指定したファイルが `start` 時に使用されます。"
    "--model_img_width <モデルのINPUTサイズ(横px)>","","AIモデルのINPUTサイズ(横px)を指定します"
    "--model_img_height <モデルのINPUTサイズ(縦px)>","","AIモデルのINPUTサイズ(縦px)を指定します"
    "--predict_type <推論タイプ>","〇","AIモデルの推論タイプを指定します。 :ref:`参照<predict_type_list>` "
    "--custom_predict_py <カスタム推論pyファイル>","","独自の推論タイプを作成するときに指定。この時は `--predict_type Custom` を指定"
    "--label_file <ラベルファイル>","","推論結果のクラスラベルファイルを指定。改行区切りでラベル名(行indexがクラスと一致する)を指定したファイル。"
    "--color_file <色ファイル>","","推論結果の可視化画像の色ファイルを指定。改行区切りで色(行indexがクラスと一致する)を指定したファイル。"
    "--before_injection_type <前処理タイプ>","","前処理を作成させるときに指定。参照： :doc:`./injections` "
    "--before_injection_py <前処理pyファイル>","","独自の前処理を作成するときに指定"
    "--before_injection_conf <前処理py用設定ファイル>","","前処理に対する設定ファイルを指定"
    "--after_injection_type <後処理タイプ>","","後処理を作成させるときに指定。参照： :doc:`./injections` "
    "--after_injection_py <後処理pyファイル>","","独自の後処理を作成するときに指定"
    "--after_injection_conf <後処理py用設定ファイル>","","後処理に対する設定ファイルを指定"
    "--overwrite","","デプロイ済みであっても上書きする指定"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間を指定"


.. _predict_type_list:

クライアント(推論タイプ一覧) : `iinfer -m client -c predict_type_list <Option>`
================================================================================

推論タイプ一覧を出力します。オプションの指定はありません。


クライアント(推論の実行) : `iinfer -m client -c predict <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "-i,--input_file <推論対象の画像ファイル>","","推論させる画像をファイルで指定します"
    "--stdin","","推論させる画像を標準入力から読み込む"
    "--nodraw","","推論結果画像にbbox等の描き込みを行わない"
    "--pred_input_type <推論対象の入力タイプ>","","推論させる入力タイプを指定します。指定可能な入力タイプは `bmp` , `png` , `jpeg` , `capture` , `output_json` "
    "--output_image <推論結果画像の保存先ファイル>","","推論結果画像の保存先ファイルを指定します"
    "-P,--output_preview","","推論結果画像を `cv2.imshow` で表示します"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"


クライアント(ディレクトリ内の画像ファイルを取得) : `iinfer -m client -c read_dir <Option>`
================================================================================================

このコマンドは、パイプで接続して下記のように使用します。

.. code-block:: bat

   iinfer -m client -c read_dir <Option> | iinfer -m client -c predict --stdin --pred_image_type capture <Option>

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--glob_str <globパターン>","〇","読込むファイルのglobパターンを指定する。"
    "--read_input_type <読込む画像のタイプ>","","読込む画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` , `filelist` "
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--root_dir <ルートディレクトリ>","","検索の基準となるルートディレクトリを指定する。"
    "--include_hidden","","読込むファイルの種類に隠しファイルを含めるかどうかを指定する。"
    "--moveto <移動する先のディレクトリ>","","読み込んだファイルを移動する先のディレクトリを指定する。"
    "--polling","","定期的にディレクトリ内の読込みを繰り返すかどうかを指定する。"
    "--polling_count <繰り返し回数>","","ディレクトリ内の読込みの繰り返し回数を指定する。"
    "--polling_interval <繰り返し間隔>","","ディレクトリ内の読込みの繰り返し間隔(秒)を指定する。"
    "--output_csv <処理結果csvの保存先ファイル>","","キャプチャーした内容をcsvで保存します。これを指定した場合、標準出力は行いません。"
    "-o, --output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, --output_json_append","","このオプションは使用できません"


クライアント(AIモデルの起動) : `iinfer -m client -c start <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "--model_provider <モデルプロバイダー>","","ONNX形式のモデルファイルの場合に指定可能。指定可能なプロバイダーは `CPUExecutionProvider` , `CUDAExecutionProvider` , `TensorrtExecutionProvider` "
    "--use_track","","ObjectDetectionタスクの場合に指定可能。motpyを使ってトラッキングID付与を行う"
    "--gpuid <GPUのid>","","GPUのディバイスIDを指定します。"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"


クライアント(AIモデルの停止) : `iinfer -m client -c stop <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"


.. _train_type_list:

クライアント(学習タイプ一覧) : `iinfer -m client -c train_type_list <Option>`
================================================================================

学習タイプ一覧を出力します。オプションの指定はありません。


クライアント(AIモデルの学習) : `iinfer -m client -c train <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "--overwrite","","学習済みであっても上書きする指定"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間を指定"


クライアント(AIモデルの配備解除) : `iinfer -m client -c undeploy <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定します"
    "--retry_count <リトライ回数>","","Redisサーバーへの再接続回数を指定。0以下を指定すると永遠に再接続を行う。"
    "--retry_interval <リトライ間隔>","","Redisサーバーに再接続までの秒数を指定"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

