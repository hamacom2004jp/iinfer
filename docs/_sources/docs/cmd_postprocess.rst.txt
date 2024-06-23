.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（postprocessモード）
****************************************************

- postprocessモードのコマンド一覧です。

後処理(画像分類判定) : `iinfer -m postprocess -c cls_jadge <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--ok_score_th","","クラススコアがこの値以上のものはok判定されます"
    "--ok_classes","`ok_score_th` を指定する場合は `ok_classes` か `ok_labels` が〇","okクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ok_labels","`ok_score_th` を指定する場合は `ok_classes` か `ok_labels` が〇","okクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--ng_score_th","","クラススコアがこの値以上のものはng判定されます"
    "--ng_classes","`ng_score_th` を指定する場合は `ng_classes` か `ng_labels` が〇","ngクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ng_labels","`ng_score_th` を指定する場合は `ng_classes` か `ng_labels` が〇","ngクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--ext_score_th","","クラススコアがこの値以上のものはgray判定されます"
    "--ext_classes","`ext_score_th` を指定する場合は `ext_classes` か `ext_labels` が〇","grayクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ext_labels","`ext_score_th` を指定する場合は `ext_classes` か `ext_labels` が〇","grayクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--output_image <後処理結果画像の保存先ファイル>","","後処理結果画像の保存先ファイルを指定します"
    "--nodraw","","推論結果画像にbbox等の描き込みを行いません。"
    "-P,--output_preview","","判定結果画像を`cv2.imshow`で表示します。"


後処理(CSV出力) : `iinfer -m postprocess -c csv <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--out_headers","","出力するヘッダーを指定します。複数指定できます。"
    "--noheader","","ヘッダー行の出力を行いません。"
    "--output_csv <処理結果csvの保存先ファイル>","","内容をcsvで保存します。これを指定した場合、標準出力は行いません。"
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"
    "-f,--format","","このコマンドではこのオプションは無視されます。"


後処理(物体検知個所切り出し) : `iinfer -m postprocess -c det_clip <Option>`
==============================================================================

ObjectDetectionで検知した個所を切り出し、caprute形式のcsvで出力します。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定します。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--clip_margin <マージン幅>","","検視したbboxの周囲に余白を設けるピクセル数です。但し、元画像の外側に余白が出る場合は、確保できるだけ余白を取得します。"
    "--output_csv <処理結果csvの保存先ファイル>","","内容をcsvで保存します。これを指定した場合、標準出力は行いません。"
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"
    "-f,--format","","このコマンドではこのオプションは無視されます。"

後処理(顔認識用ストアファイル生成) : `iinfer -m postprocess -c det_face_store <Option>`
==============================================================================================

Face Detection and Recognitionで検知した顔特徴データを個所を切り出し、顔認識ストアファイルを生成します。顔認識ストアファイルの使用方法は以下のとおりです。
1. 生成したファイルをテキストエディタで開き、face_label項目に名前を入力します。
2. 生成したファイルを `client` モードの `deploy` コマンドの `--model_conf_file` オプションに指定し、上書きデプロイします。
3. デプロイしたモデルを `client` モードの `start` コマンドで起動します。
4. 起動したモデルに対して、 `client` モードの `predict` コマンドで推論を実行します。
5. 推論結果の `output_labels` に顔認識結果が出力されます。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定します。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--face_threshold <顔スコアに対する閾値>","","顔スコアが閾値以下の場合は、顔特徴量ストアに含まれないようにします。※1"
    "--clip_margin <マージン幅>","","検視したbboxの周囲に余白を設けるピクセル数です。但し、元画像の外側に余白が出る場合は、確保できるだけ余白を取得します。"
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"

- ※1 : 顔特徴量ストアに登録されている顔特徴量と、推論結果の顔特徴量との差が顔スコアになります。


後処理(物体検知フィルター) : `iinfer -m postprocess -c det_filter <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--score_th","","bboxのクラススコアがこの値以下のものは除去します。"
    "--width_th","","bboxの横幅がこの長さ以下のものは除去します。"
    "--height_th","","bboxの縦幅がこの長さ以下のものは除去します。"
    "--classes","","このクラス以外のbboxは除去します。複数指定できます。"
    "--labels","","このラベル以外のbboxは除去します。複数指定できます。"
    "--output_image <後処理結果画像の保存先ファイル>","","後処理結果画像の保存先ファイルを指定します"
    "--nodraw","","推論結果画像にbbox等の描き込みを行いません。"
    "-P,--output_preview","","推論結果画像を`cv2.imshow`で表示します。"

後処理(物体検知判定) : `iinfer -m postprocess -c det_jadge <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--ok_score_th","","クラススコアがこの値以上のものはok判定されます"
    "--ok_classes","`ok_score_th` を指定する場合は `ok_classes` か `ok_labels` が〇","okクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ok_labels","`ok_score_th` を指定する場合は `ok_classes` か `ok_labels` が〇","okクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--ng_score_th","","クラススコアがこの値以上のものはng判定されます"
    "--ng_classes","`ng_score_th` を指定する場合は `ng_classes` か `ng_labels` が〇","ngクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ng_labels","`ng_score_th` を指定する場合は `ng_classes` か `ng_labels` が〇","ngクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--ext_score_th","","クラススコアがこの値以上のものはgray判定されます"
    "--ext_classes","`ext_score_th` を指定する場合は `ext_classes` か `ext_labels` が〇","grayクラスに含めるクラスindexを指定します。複数指定できます。"
    "--ext_labels","`ext_score_th` を指定する場合は `ext_classes` か `ext_labels` が〇","grayクラスに含めるクラスラベルを指定します。複数指定できます。"
    "--output_image <後処理結果画像の保存先ファイル>","","後処理結果画像の保存先ファイルを指定します"
    "--nodraw","","推論結果画像にbbox等の描き込みを行いません。"
    "-P,--output_preview","","判定結果画像を`cv2.imshow`で表示します。"


後処理(HTTPリクエストの実行) : `iinfer -m postprocess -c httpreq <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--json_without_img","",JSONの送信時に画像を含めず送信します。"
    "--json_connectstr <URL>","〇","推論結果のJSONのPOST先URLを指定します。"
    "--img_connectstr <URL>","","推論結果の画像のPOST先URLを指定します。"
    "--text_connectstr <URL>","","推論結果のテキストのPOST先URLを指定します。"
    "--fileup_name <パラメータ名>","","推論結果の画像をPOSTするときのパラメータ名を指定します。省略すると `file` が使用されます。"
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"


後処理(領域ボックス検知) : `iinfer -m postprocess -c seg_bbox <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--del_segments","","セグメンテーションマスクを結果から削除します。結果容量削減に効果があります。"
    "--output_image <後処理結果画像の保存先ファイル>","","後処理結果画像の保存先ファイルを指定します"
    "--nodraw","","推論結果画像にbbox等の描き込みを行いません。"
    "--nodraw_bbox","","推論結果画像にbboxの描き込みを行いません。"
    "--nodraw_rbbox","","推論結果画像に回転bboxの描き込みを行いません。"
    "-P,--output_preview","","推論結果画像を`cv2.imshow`で表示します。"


後処理(領域検知フィルター) : `iinfer -m postprocess -c seg_filter <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--logits_th","","ピクセルごとのクラススコアがこの値以下のものは除去されます"
    "--classes","","このクラス以外のマスクは除去します。複数指定できます。"
    "--labels","","このラベル以外のマスクは除去します。複数指定できます。"
    "--output_image <後処理結果画像の保存先ファイル>","","後処理結果画像の保存先ファイルを指定します"
    "--nodraw","","推論結果画像にマスクの描き込みを行いません。"
    "--del_logits","","セグメンテーションスコアを結果から削除します。結果容量削減に効果があります。"
    "-P,--output_preview","","推論結果画像を`cv2.imshow`で表示します。"


後処理(showimg転送) : `iinfer -m postprocess -c showimg <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します。"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します。"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "--maxrecsize <最大レコードサイズ>","","Redisサーバーに保存する推論結果の最大レコードサイズを指定します。"


