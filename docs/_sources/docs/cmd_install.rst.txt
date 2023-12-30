.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（installモード）
****************************************************

- installモードのコマンド一覧です。
- `iinfer` をインストールした直後にはAIフレームワークのインストールがされていない状態です。
- 通常推論サーバー側にしかAIフレームワークが必要ないため、任意でインストールする必要があります。

インストール(onnx) : `iinfer -m install -c onnx`
==============================================================================

`onnxruntime` をインストールします。オプションの指定はありません。


インストール(mmdet) : `iinfer -m install -c mmdet`
==============================================================================

`mmdetection` をインストールします。オプションの指定はありません。

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
- このコマンドで作成されるdockerイメージには、上記 `onnxruntime` と `mmdetection` が含まれます。
- `build` が成功すると、実行時ディレクトリに `docker-compose.yml` ファイルが生成されます。
- サーバーを起動させるには、 `docker-compose.yml` ファイルがある場所で `docker-compose up -d` を実行してください。
- サーバーを停止させるには、 `docker-compose.yml` ファイルがある場所で `docker-compose down` を実行してください。
- windows環境ではこのコマンドは未サポートです。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <データディレクトリ>","","省略した時は `$HONE/.iinfer` を使用します。"
