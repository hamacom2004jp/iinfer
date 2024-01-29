.. -*- coding: utf-8 -*-

****************************************************
サーバー環境構築
****************************************************

- `iinfer` を使用して各種AIフレームワークをインストールしたDockerイメージを構築することが出来ます。
- 物体検知を実行するための手順を解説します。

１．サーバー環境を構築する（Ubuntu上で実行）
=============================================================================

- `iinfer -m install -c server <Option>` コマンドでサーバー環境を構築できます。
    - `--install_mmdet` オプションは `mmdetection` のみをDockerイメージに含めるための指定です。
    - `--install_mmdet` オプションを使用しない場合は、デフォルトのフレームワークがインストールされます。 :doc:`./cmd_install` を参照してください。
    - `--install_tag mmdet` は、作成するイメージ名やコンテナ名、 `iinfer` 推論サーバーの名前に使用されるタグ名です。

    .. code-block:: bash

         $ iinfer -m install -c server --install_mmdet --install_tag mmdet

- 上記のコマンドを実行すると、以下のようなDockerイメージが作成されます。
  
    .. code-block:: bash

         $ docker images
         REPOSITORY       TAG                IMAGE ID       CREATED             SIZE
         hamacom/iinfer   0.5.6_mmdet        4a501392d33e   About a minute ago  9.54GB
         ubuntu/redis     latest             4603cee0d86e   About a minute ago  110MB

- また、実行時のディレクトリに `docker-compose.yml` が作成されますので、下記のコマンドで推論サーバーを起動できます。

    .. code-block:: bash

         $ docker-compose up -d
         Creating network "ubuntu_backend" with driver "bridge"
         Creating iinfer_server_mmdet      ... done
         Creating redis                    ... done

- 続けて顔認識の推論サーバーを下記のコマンドで構築してみます。

    .. code-block:: bash

         $ iinfer -m install -c server --install_insightface --install_tag face

- 作成されたDockerイメージは以下のようになります。

    .. code-block:: bash

         $ docker images
         REPOSITORY       TAG                IMAGE ID       CREATED             SIZE
         hamacom/iinfer   0.5.6_mmdet        4a501392d33e   8 minutes ago       9.54GB
         hamacom/iinfer   0.5.6_face         43fcfe20c33f   About a minute ago  1.91GB
         ubuntu/redis     latest             4603cee0d86e   8 minutes ago       110MB

- 推論サーバーを再起動させます。

    .. code-block:: bash

         $ docker-compose down
         Stopping redis                    ... done
         Stopping iinfer_server_mmdet      ... done
         Removing redis                    ... done
         Removing iinfer_server_mmdet      ... done
         Removing network ubuntu_backend
         $
         $ docker-compose up -d
         Creating network "ubuntu_backend" with driver "bridge"
         Creating iinfer_server_mmdet      ... done
         Creating iinfer_server_face       ... done
         Creating redis                    ... done

- `iinfer -m server -c list -f` コマンドで推論サーバーの一覧を表示できます。

    .. code-block:: bash

         $ iinfer -m server -c list -f
         | svname            |   recive_cnt |   sccess_cnt |   warn_cnt |   error_cnt |
         |-------------------|--------------|--------------|------------|-------------|
         | server_mmdet      |            0 |            0 |          0 |           0 |
         | server_face       |            0 |            0 |          0 |           0 |
         0.020 seconds.


２．推論サーバーに接続する
=============================================================

- `iinfer -m client -c deploy_list <Option>` コマンドで推論サーバー接続を試してみます。
- `--svname server_mmdet` コマンドで推論サーバー名を指定しています。

    .. code-block:: bash

         $ iinfer -m client -c deploy_list --svname server_mmdet

