.. -*- coding: utf-8 -*-

******************
インジェクション
******************

- iinferのサーバー処理に、任意の処理を追加することが出来ます。
- Segmentaionなどの処理の場合、推論結果のサイズが大きいため、サーバー側で不要な推論結果をフィルタすることが有効です。
- iinferクライアントの後処理として同様のことが行えますが、サーバー側で処理することで、クライアント側の処理を軽減できます。
- インジェクションには、 `before` と `after` の2つのインジェクションポイントがあります。
- インジェクションの指定は、 `client` モードの `deploy` コマンドのオプションで行います。


クライアント(AIモデルの配備) ※抜粋 : `iinfer -m client -c deploy <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--before_injection_type <前処理タイプ>","","前処理を作成するときに指定。 :ref:`参照<before_injection_type_list>` "
    "--before_injection_py <前処理pyファイル>","","独自の前処理を作成するときに指定"
    "--before_injection_conf <前処理py用設定ファイル>","","前処理に対する設定ファイルを指定"
    "--after_injection_type <後処理タイプ>","","後処理を作成するときに指定。 :ref:`参照<after_injection_type_list>` "
    "--after_injection_py <後処理pyファイル>","","独自の後処理を作成するときに指定"
    "--after_injection_conf <後処理py用設定ファイル>","","後処理に対する設定ファイルを指定"


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

- `after_cmd_injection`

    .. csv-table::
        :widths: 20, 10, 70
        :header-rows: 1

        "Option","Type","Description"
        "cmdline","str","実行するコマンド。設定される環境変数は `outputs` , `output_image` 。この値は一時ファイルのファイルパス。"
        "output_image_ext","str","出力画像のフォーマットを指定します。指定可能な画像タイプは `bmp` , `png` , `jpeg`"
        "output_maxsize","int","コマンド実行結果をキャプチャーする最大サイズ"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "cmdline": "pwd",
            "output_image_ext": "jpeg",
            "output_maxsize": 5242880
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
        "json_without_img","bool","画像を含まないJSONをPOSTする場合True"

    .. code-block:: json

        /** サンプル設定ファイル **/
        {
            "outputs_url": "http://localhost:8081/showimg/pub_img",
            "output_image_url": "http://localhost:8081/showimg/pub_img",
            "output_image_ext": "jpeg",
            "output_image_prefix": "output_",
            "json_without_img": true
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

- `after_showimg_injection`
    
        .. csv-table::
            :widths: 20, 10, 70
            :header-rows: 1
    
            "Option","Type","Description"
            "host","str","Redisサーバーのサービスホストを指定します。省略時は localhost を使用します"
            "port","int","Redisサーバーのサービスポートを指定します。省略時は 6379 を使用します"
            "password","str","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は password を使用します"
            "svname","str","推論サーバーのサービス名を指定します。省略時は server を使用します"
            "maxrecsize","int","推論結果の最大レコードサイズを指定します。省略時は 1000 を使用します"

        .. code-block:: json
    
            /** サンプル設定ファイル **/
            {
                "host": "localhost",
                "port": "6379",
                "password": "password",
                "svname": "server",
                "maxrecsize": 1000
            }