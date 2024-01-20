.. -*- coding: utf-8 -*-

****************************************************
物体検知（ Object Detection ）
****************************************************

- `iinfer` を使用して物体検知の仕組みを作成することが出来ます。
- 物体検知を実行するための手順を解説します。

１．物体検知モデル(mmdetection)の環境をインストールする（通常Ubuntu上で実行）
=============================================================================

- `iinfer -m install -c server <Option>` コマンドで顔認識モデルの環境をインストールしてください。

    .. code-block:: bash

         $ iinfer -m install -c server --install_mmdet --install_tag mmdet

- `docker-compose` コマンドで顔認識モデルのサーバーを起動してください。

    .. code-block:: bash

         $ docker-compose -f docker-compose_mmdet.yml up -d

２．物体検知モデルをデプロイする（通常Windows上で実行）
=============================================================

- :doc`./models` の `Object Detection` の項目に記載されているモデルをダウンロードしてください。
- `iinfer -m client -c deploy <Option>` コマンドで顔検出モデルを配備してください。
    - mmdetection の場合``

    .. code-block:: bash

         $ iinfer -m client -c deploy --name mmdet_det_YoloX --model_file yolox_x_8x8_300e_coco_20211126_140254-1ef88d67.pth --model_conf_file yolox_x_8xb8-300e_coco.py --model_conf_file yolox_s_8xb8-300e_coco.py --model_conf_file yolox_tta.py --predict_type mmdet_det_YoloX --label_file label_coco.txt

- `iinfer -m client -c start <Option>` コマンドでAIモデルの起動を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c start --name mmdet_det_YoloX

３．物体検知を実行する
==============================

- `iinfer -m client -c predict <Option>` コマンドで物体検知が行えるようになります。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --output_preview > /dev/null

４．検知したbboxをフィルターする
================================

- `iinfer -m postprocess -c det_filter <Option>` コマンドで検知したbboxのフィルターが行えるようになります。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --nodraw | iinfer -m postprocess -c det_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview > /dev/null

５．検知したbboxの内容から画像判定する
=======================================

- `iinfer -m postprocess -c det_jadge <Option>` コマンドで検知したbboxの内容から画像判定が行えます。製造業における良否判定などに利用できます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --nodraw | iinfer -m postprocess -c det_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview | iinfer -m postprocess -c det_jadge --stdin --ok_score_th 0.5 --ok_labels person --ng_score_th 0.3 --ng_labels dog --output_preview > /dev/null

６．画像判定をCSV形式で出力する
=======================================

- `iinfer -m postprocess -c csv <Option>` コマンドで判定結果をCSV形式で出力できます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmdet_det_YoloX --image_type capture --stdin --nodraw | iinfer -m postprocess -c det_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview | iinfer -m postprocess -c det_jadge --stdin --ok_score_th 0.5 --ok_labels person --ng_score_th 0.3 --ng_labels dog --output_preview | iinfer -m postprocess -c csv --stdin
