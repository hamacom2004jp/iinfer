.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（installモード）
****************************************************

- installモードのコマンド一覧です。
- `iinfer` をインストールした直後にはAIフレームワークのインストールがされていない状態です。
- 通常推論サーバー側にしかAIフレームワークが必要ないため、任意でインストールする必要があります。


インストール(insightface) : `iinfer -m install -c insightface`
==============================================================================

`insightface` をインストールします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"


インストール(mmcls) : `iinfer -m install -c mmcls`
==============================================================================

`mmcls` をインストールします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"


インストール(mmdet) : `iinfer -m install -c mmdet`
==============================================================================

`mmdetection` をインストールします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"


インストール(mmpretrain) : `iinfer -m install -c mmpretrain`
==============================================================================

`mmpretrain` をインストールします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"


インストール(mmseg) : `iinfer -m install -c mmseg`
==============================================================================

`mmsegmentation` をインストールします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"


インストール(onnx) : `iinfer -m install -c onnx`
==============================================================================

`onnxruntime` をインストールします。オプションの指定はありません。


インストール(redis) : `iinfer -m install -c redis <Option>`
==============================================================================

`redis-server` のdockerイメージをPULLします。オプションは以下の通りです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--wsl_name <ディストリビューション名>","Windowsの場合は〇","Windowsの場合はWSLのディストリビューションの名前を指定します。"
    "--wsl_user <user名>","Windowsの場合は〇","Windowsの場合はWSL内のユーザー名を指定します。"


インストール(server) : `iinfer -m install -c server <Option>`
==============================================================================

- `推論サーバー` のdockerイメージを `build` します。オプションは以下の通りです。
- `build` が成功すると、実行時ディレクトリに `docker-compose.yml` ファイルが生成されます。
- サーバーを起動させるには、 `docker-compose.yml` ファイルがある場所で `docker-compose up -d` を実行してください。
- サーバーを停止させるには、 `docker-compose.yml` ファイルがある場所で `docker-compose down` を実行してください。
- windows環境ではこのコマンドは未サポートです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <データフォルダ>","","省略した時は `$HONE/.iinfer` を使用します。"
    "--install_iinfer <iinferモジュール名>","","省略した時は `iinfer` を使用します。 `iinfer==0.10.7` といった指定も可能です。"
    "--install_cmdbox <cmdboxモジュール名>","","省略した時は `cmdbox` を使用します。 `cmdbox==0.4.5` といった指定も可能です。"
    "--install_onnx","","dockerイメージ内に `onnxruntime` をインストールします。"
    "--install_mmdet","","dockerイメージ内に `mmdetection` をインストールします。"
    "--install_mmseg","","dockerイメージ内に `mmsegmentation` をインストールします。"
    "--install_mmcls","","dockerイメージ内に `mmclassification` をインストールします。※1"
    "--install_mmpretrain","","dockerイメージ内に `mmpretrain` をインストールします。"
    "--install_insightface","","dockerイメージ内に `insightface` をインストールします。"
    "--install_no_python","","dockerイメージ内に `python` をインストールしません。"
    "--install_from <イメージ名>","","作成するdockerイメージの元となるFROMイメージを指定します。"
    "--install_tag <追加のタグ名>","","指定すると作成するdockerイメージのタグ名に追記出来ます。"
    "--install_use_gpu","","GPUを使用するモジュール構成でインストールします。"
    

- ※1 : `mmclassification` と `mmpretrain` はバージョンによって共存できない場合があります。
