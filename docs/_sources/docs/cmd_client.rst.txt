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
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名(任意)を指定する"
    "--model_file <モデルファイル>","〇","学習済みのモデルファイルを指定する"
    "--model_conf_file <モデル設定ファイル>","","mmlabの場合はモデル設定ファイルを指定する。複数指定可能ですが、最初に指定したファイルが `start` 時に使用されます。"
    "--model_img_width <モデルのINPUTサイズ(横px)>","","AIモデルのINPUTサイズ(横px)を指定する"
    "--model_img_height <モデルのINPUTサイズ(縦px)>","","AIモデルのINPUTサイズ(縦px)を指定する"
    "--predict_type <推論タイプ>","〇","AIモデルの推論タイプを指定する。 :ref:`参照<predict_type_list>` "
    "--custom_predict_py <カスタム推論pyファイル>","","独自の推論タイプを作成するときに指定。この時は `--predict_type Custom` を指定"
    "--label_file <ラベルファイル>","","推論結果のクラスラベルファイルを指定。改行区切りでラベル名(行indexがクラスと一致する)を指定したファイル。"
    "--color_file <色ファイル>","","推論結果の可視化画像の色ファイルを指定。改行区切りで色(行indexがクラスと一致する)を指定したファイル。"
    "--before_injection_type <前処理タイプ>","","前処理を作成するときに指定。 :ref:`参照<before_injection_type_list>` "
    "--before_injection_py <前処理pyファイル>","","独自の前処理を作成するときに指定"
    "--before_injection_conf <前処理py用設定ファイル>","","独自の前処理に対する設定ファイルを指定"
    "--after_injection_type <後処理タイプ>","","後処理を作成するときに指定。 :ref:`参照<after_injection_type_list>` "
    "--after_injection_py <後処理pyファイル>","","独自の後処理を作成するときに指定"
    "--after_injection_conf <後処理py用設定ファイル>","","独自の後処理に対する設定ファイルを指定"
    "--overwrite","","デプロイ済みであっても上書きする"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間"

.. _before_injection_type_list:

前処理タイプ設定項目一覧（ `--before_injection_type` で指定可能な値）
----------------------------------------------------------------------

- `before_grayimg_injection` を指定した場合、以下の設定項目が指定可能です。

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "-","-","設定項目はありません。"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {}


.. _after_injection_type_list:

後処理タイプ設定項目一覧（ `--after_injection_type` で指定可能な値）
--------------------------------------------------------------------

- `after_cls_jadge_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "ok_score_th","float","OK判定するbboxのスコア閾値。この値より高いスコアのbboxがあればOK判定とする"
        "ok_classes","List[str]","OK判定するbboxのクラス名。このクラスのスコアをOK判定に使用する"
        "ok_labels","List[str]","OK判定するbboxのラベル名。このラベルのスコアをOK判定に使用する"
        "ng_score_th","float","NG判定するbboxのスコア閾値。この値より高いスコアのbboxがあればNG判定とする"
        "ng_classes","List[str]","NG判定するbboxのクラス名。このクラスのスコアをNG判定に使用する"
        "ng_labels","List[str]","NG判定するbboxのラベル名。このラベルのスコアをNG判定に使用する"
        "ext_score_th","float","Gray判定するbboxのスコア閾値。この値より高いスコアのbboxがあればGray判定とする"
        "ext_classes","List[str]","Gray判定するbboxのクラス名。このクラスのスコアをGray判定に使用する"
        "ext_labels","List[str]","Gray判定するbboxのラベル名。このラベルのスコアをGray判定に使用する"
        "nodraw","bool","output_imageに描画を行わない場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "ok_score_th": 0.9,
            "ok_classes": [1],
            "ok_labels": [],
            "ng_score_th": 0.9,
            "ng_classes": [],
            "ng_labels": [],
            "ext_score_th": 0.9,
            "ext_classes": [],
            "ext_labels": [],
            "nodraw": false
        }

- `after_csv_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "out_headers","List[str]","CSV出力する項目"
        "noheader","bool","ヘッダー出力しない場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "out_headers": ["output_scores", "output_labels", "image_name"],
            "noheader": false
        }

- `after_det_filter_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "score_th","float","bboxのスコア閾値。この値より低いスコアのbboxは除外される"
        "width_th","int","bboxの横幅閾値。この値より小さいbboxは除外される"
        "height_th","int","bboxの縦幅閾値。この値より小さいbboxは除外される"
        "classes","List[str]","bboxのクラス名。この値のみのbboxが出力される"
        "labels","List[str]","bboxのラベル名。この値のみのbboxが出力される"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "score_th": 0.5,
            "width_th": 10,
            "height_th": 10,
            "classes": ["0", "1"],
            "labels": ["person", "car"]
        }

- `after_det_jadge_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "ok_score_th","float","OK判定するbboxのスコア閾値。この値より高いスコアのbboxがあればOK判定とする"
        "ok_classes","List[str]","OK判定するbboxのクラス名。このクラスのスコアをOK判定に使用する"
        "ok_labels","List[str]","OK判定するbboxのラベル名。このラベルのスコアをOK判定に使用する"
        "ng_score_th","float","NG判定するbboxのスコア閾値。この値より高いスコアのbboxがあればNG判定とする"
        "ng_classes","List[str]","NG判定するbboxのクラス名。このクラスのスコアをNG判定に使用する"
        "ng_labels","List[str]","NG判定するbboxのラベル名。このラベルのスコアをNG判定に使用する"
        "ext_score_th","float","Gray判定するbboxのスコア閾値。この値より高いスコアのbboxがあればGray判定とする"
        "ext_classes","List[str]","Gray判定するbboxのクラス名。このクラスのスコアをGray判定に使用する"
        "ext_labels","List[str]","Gray判定するbboxのラベル名。このラベルのスコアをGray判定に使用する"
        "nodraw","bool","output_imageに描画を行わない場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "ok_score_th": 0.9,
            "ok_classes": [1],
            "ok_labels": [],
            "ng_score_th": 0.9,
            "ng_classes": [],
            "ng_labels": [],
            "ext_score_th": 0.9,
            "ext_classes": [],
            "ext_labels": [],
            "nodraw": false
        }

- `after_http_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "outputs_url","str","推論結果をHTTP POSTする先のURL"
        "output_image_url","str","推論結果画像をHTTP POSTする先のURL"
        "output_image_ext","str","推論結果画像をHTTP POSTするときの画像フォーマット。指定可能なのは `bmp` , `png` , `jpeg` "
        "output_image_prefix","str","推論結果画像をHTTP POSTするときのファイル名のプレフィックス"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "outputs_url": "http://localhost:5000/outputs",
            "output_image_url": "http://localhost:5000/output_image",
            "output_image_ext": "jpeg",
            "output_image_prefix": "output_image_"
        }

- `after_seg_bbox_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "del_segments","bool","推論結果画像にbbox等の描き込みを行わない場合True"
        "nodraw","bool","output_imageにbbox等の描画を行わない場合True"
        "nodraw","bool","output_imageにbboxの描画を行わない場合True"
        "nodraw","bool","output_imageに回転bboxの描画を行わない場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "nodraw": false,
            "nodraw_bbox": false,
            "nodraw_rbbox": false,
            "del_segments": true
        }

- `after_seg_filter_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "logits_th","int","ピクセルごとのクラススコア閾値。この値以下のものは除去される"
        "classes","List[int]","bboxのクラス。この値のみのbboxが出力される"
        "labels","List[str]","bboxのラベル名。この値のみのbboxが出力される"
        "nodraw","bool","output_imageに描画を行わない場合True"
        "del_logits","bool","セグメンテーションスコアを結果から削除する場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "nodraw": false,
            "logits_th": -100.0,
            "classes": [],
            "labels": [],
            "del_logits": true
        }

クライアント(AIモデルの配備一覧) : `iinfer -m client -c deploy_list <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定する"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定する"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定する。省略時は `password` を使用する"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
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
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
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
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
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
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
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
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定する。省略時は `server` を使用する"
    "-n,--name <登録名>","〇","AIモデルの登録名を指定する"
    "-i,--input_file <推論対象の画像ファイル>","","推論させる画像をファイルで指定する"
    "--stdin","","推論させる画像を標準入力から読み込む"
    "--nodraw","","推論結果画像にbbox等の描き込みを行わない"
    "--image_type <推論対象の画像タイプ>","","推論させる画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` , `output_json` "
    "--output_image <推論結果画像の保存先ファイル>","","推論結果画像の保存先ファイルを指定する"
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
    "--output_csv <処理結果csvの保存先ファイル>","","キャプチャーした内容をcsvで保存する。これを指定した場合、標準出力は行いません。"
    "-o, --output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, --output_json_append","","このオプションは使用できません"
