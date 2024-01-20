.. -*- coding: utf-8 -*-

****************************************************
パイプライン
****************************************************

- `iinfer` の多くのコマンドは、パイプライン処理を行えるように作られています。
- パイプライン処理あ、コマンドの出力を次のコマンドの入力として渡すことが出来る機能です。
- この機能を使用することで、複数のコマンドを繋げて実行することが出来ます。
- 下記の例は、キャプチャーした画像を、物体検知の推論を行い、bboxのフィルタ、画像判定、CSV出力という流れでパイプライン処理を行っている例です。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --nodraw | iinfer -m postprocess -c det_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview | iinfer -m postprocess -c det_jadge --stdin --ok_score_th 0.5 --ok_labels person --ng_score_th 0.3 --ng_labels dog --output_preview | iinfer -m postprocess -c csv --stdin

- 前のコマンドが出力した内容を入力として受け付けるには、 `--stdin` オプションを指定します。

- しかし、スクリプトの作り方によっては、パイプでつなぐのではなく一度ファイルに出力する方が良い場合もあります。
- その場合は、 `--output_json <出力ファイル名>` オプションを使用することで、処理結果を指定したファイルに出力することが出来ます。
- なお、 `--output_json_append` オプションを使用することで、ファイルに追記することも出来ます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --nodraw --output_json pred.json

- `--output_json <出力ファイル名>` で出力した結果を、別のコマンドの入力として使用する場合は、 `--input_file <入力ファイル名>` オプションを使用します。

    .. code-block:: bash

         $ iinfer -m postprocess -c det_filter --score_th 0.1 --labels dog --labels person --output_preview --input_file pred.json
