.. -*- coding: utf-8 -*-

****************************************************
領域検知（ Segmentation ）
****************************************************

- `iinfer` を使用して領域検知の仕組みを作成することが出来ます。
- 領域検知を実行するための手順を解説します。

１．領域検知モデル(segmentation)の環境をインストールする（通常Ubuntu上で実行）
===============================================================================

- `iinfer -m install -c server <Option>` コマンドで領域検知モデルの環境をインストールしてください。

    .. code-block:: bash

         $ iinfer -m install -c server --install_mmseg --install_tag mmseg

- `docker-compose` コマンドで領域検知モデルのサーバーを起動してください。

    .. code-block:: bash

         $ docker-compose -f docker-compose_mmseg.yml up -d

２．領域検知モデルをデプロイする（通常Windowsから実行）
=============================================================

- :doc:`./models` の `Object Detection` の項目に記載されているモデルをダウンロードしてください。
- `iinfer -m client -c deploy <Option>` コマンドで領域検知モデルを配備してください。
    - mmdetection の場合``

    .. code-block:: bash

         $ iinfer -m client -c deploy --name mmseg_seg_PSPNet --model_file pspnet_r18-d8_512x1024_80k_cityscapes_20201225_021458-09ffa746.pth --model_conf_file pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py --model_conf_file pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py --predict_type mmseg_seg_PSPNet

- `iinfer -m client -c start <Option>` コマンドでAIモデルの起動を行ってください。

    .. code-block:: bash

         $ iinfer -m client -c start --name mmseg_seg_PSPNet

３．領域検知を実行する（通常Windowsから実行）
=============================================================

- `iinfer -m client -c predict <Option>` コマンドで領域検知が行えます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmseg_seg_PSPNet --image_type capture --stdin --output_preview > /dev/null

４．検知した領域をフィルターする（通常Windowsから実行）
=============================================================

- `iinfer -m postprocess -c seg_filter <Option>` コマンドで検知した領域のフィルターが行えます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmseg_seg_PSPNet --image_type capture --stdin --nodraw | iinfer -m postprocess -c seg_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview > /dev/null

５．検知した領域の内容から画像判定する（通常Windowsから実行）
=============================================================

- `iinfer -m postprocess -c det_jadge <Option>` コマンドで検知した領域の内容から画像判定が行えます。製造業における良否判定などに利用できます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmseg_seg_PSPNet --image_type capture --stdin --nodraw | iinfer -m postprocess -c seg_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview | iinfer -m postprocess -c seg_jadge --stdin --ok_score_th 0.5 --ok_labels person --ng_score_th 0.3 --ng_labels dog --output_preview > /dev/null

６．画像判定をCSV形式で出力する（通常Windowsから実行）
=============================================================

- `iinfer -m postprocess -c csv <Option>` コマンドで判定結果をCSV形式で出力できます。

    .. code-block:: bash

         $ iinfer -m client -c capture --image_type capture | iinfer -m client -c predict --name mmseg_seg_PSPNet --image_type capture --stdin --nodraw | iinfer -m postprocess -c seg_filter --stdin --score_th 0.1 --labels dog --labels person --output_preview | iinfer -m postprocess -c seg_jadge --stdin --ok_score_th 0.5 --ok_labels person --ng_score_th 0.3 --ng_labels dog --output_preview | iinfer -m postprocess -c csv --stdin
