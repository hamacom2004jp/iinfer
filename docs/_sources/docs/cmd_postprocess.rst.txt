.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（postprocessモード）
****************************************************

- postprocessモードのコマンド一覧です。

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
    "--nodraw","","推論結果画像にbbox等の描き込みを行いません。"
    "-P,--output_preview","","判定結果画像を`cv2.imshow`で表示します。"

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
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"
    "-f,--format","","このコマンドではこのオプションは無視されます。"

後処理(HTTPリクエストの実行) : `iinfer -m postprocess -c httpreq <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-i,--input_file <推論結果ファイル>","`--stdin` を指定しない場合〇","後処理させる推論結果をファイルで指定します。"
    "--stdin","`--input_file` を指定しない場合〇","後処理させる推論結果を標準入力から読み込みます。"
    "--json_connectstr <URL>","〇","推論結果のJSONのPOST先URLを指定します。"
    "--img_connectstr <URL>","","推論結果の画像のPOST先URLを指定します。"
    "--fileup_name <パラメータ名>","","推論結果の画像をPOSTするときのパラメータ名を指定します。省略すると `file` が使用されます。"
    "-o, -output_json <処理結果jsonの保存先ファイル>","","このオプションは使用できません"
    "-a, -output_json_append","","このオプションは使用できません"
