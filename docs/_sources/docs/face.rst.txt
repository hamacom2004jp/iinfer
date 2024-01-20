.. -*- coding: utf-8 -*-

****************************************************
顔認識（ Face Detection and Recognition ）
****************************************************

- `iinfer` を使用して顔認識の仕組みを作成することが出来ます。
- 顔認識を実行するための手順を解説します。

１．顔認識モデルの環境をインストールする（通常Ubuntu上で実行）
=======================================================================

- `iinfer -m install -c server <Option>` コマンドで顔認識モデルの環境をインストールしてください。

    .. code-block:: bash

         $ iinfer -m install -c server --install_insightface --install_tag face

- `docker-compose` コマンドで顔認識モデルのサーバーを起動してください。

    .. code-block:: bash

         $ docker-compose -f docker-compose_face.yml up -d


２．顔認識モデルをデプロイする（通常Windows上で実行）
=============================================================

- :doc`./models` の `Face Detection and Recognition` の項目に記載されているモデルをダウンロードしてください。
- `iinfer -m client -c deploy <Option>` コマンドで顔検出モデルを配備してください。

    .. code-block:: bash

         $ iinfer -m client -c deploy --name insightface_det --model_file buffalo_sc.zip --predict_type insightface_det

- `iinfer -m client -c capture <Option>` コマンドで顔認識させたい人の顔画像をキャプチャーしてください。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture --capture_count 1 --output_csv cap.csv

- `iinfer -m client -c start <Option>` コマンドでAIモデルの起動を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c start --name insightface_det

- `iinfer -m client -c predict <Option>` コマンドで顔検出を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c predict --name insightface_det --input_file cap.csv --image_type capture --output_json pred.json

- `iinfer -m postprocess -c det_face_store <Option>` コマンドで顔認識ストアを生成してください。 `--output_json store.json` で出力先の認証ファイルを指定しています。

    .. code-block:: bash

         $ iinfer -m postprocess -c det_face_store --input_file pred.json --image_type capture --output_json store.json

- `iinfer -m client -c stop <Option>` コマンドでAIモデルの停止を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c stop --name insightface_det

３．顔認識ストアを編集及びデプロイする（通常Windows上で実行）
=============================================================

- 上の手順で作成した顔認識ストアを開き、ラベルを記入します。 `face_label` に人の名前を記入し保存します。

    .. code-block:: json

        {"success": [{"face_label": "", "face_embedding": "tZmA....vDL8=", "face_embedding_dtype": "float32", "face_embedding_shape": [512], "face_image_type": "capture", "face_image_shape": [123, 93, 3], "face_image": "jYTU....Ijcx="}]}


- `iinfer -m client -c deploy <Option>` コマンドで顔認識ストアを配備（上書きデプロイ）してください。 `--model_conf_file store.json` で登録する認証ファイルを指定しています。

    .. code-block:: bash

         $ iinfer -m client -c deploy --name insightface_det --model_file buffalo_sc.zip --model_conf_file store.json --predict_type insightface_det --overwrite

４．顔認識を実行する（通常Windows上で実行）
=============================================================

- `iinfer -m client -c start <Option>` コマンドでAIモデルの起動を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c start --name insightface_det

- `iinfer -m client -c predict <Option>` コマンドで顔検出&顔認識が行えるようになります。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name insightface_det --image_type capture --stdin --output_preview > /dev/null

