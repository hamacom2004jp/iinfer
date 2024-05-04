.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（redisモード）
****************************************************

- redisモードのコマンド一覧です。

Redisサーバー起動 : `iinfer -m redis -c docker_run <Option>`
==============================================================================

- installモードで `iinfer -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します。"
    "--password <パスワード>","","Redisサーバーのアクセスパスワードを指定します。省略時は`password`を使用します。"
    "--wsl_name <ディストリビューション名>","Windowsの場合は〇","Windowsの場合はWSLのディストリビューションの名前を指定します。"
    "--wsl_user <user名>","Windowsの場合は〇","Windowsの場合はWSL内のユーザー名を指定します。"

Redisサーバー停止 : `iinfer -m redis -c docker_stop <Option>`
==============================================================================

- installモードで `iinfer -m install -c server` を実行している場合は、 `docker-compose down` を使用してください。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--wsl_name <ディストリビューション名>","Windowsの場合は〇","Windowsの場合はWSLのディストリビューションの名前を指定します。"
    "--wsl_user <user名>","Windowsの場合は〇","Windowsの場合はWSL内のユーザー名を指定します。"
