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

****************************************************
GPU環境構築
****************************************************

- サーバー環境にGPUを搭載した場合、GPU環境を構築することが出来ます。
- なおこの手順はNVIDIA製のGPUを使用する場合の手順です。

CUDA + cuDNNのインストール
==============================================

1. Windowsの場合 `Build Tools for Visual Studio 2022 <https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/>`__ をインストールします。
    1. インストールするモジュールは以下の通りです。環境によって必要なものが異なる場合があります。
        - C++ 2022 再配布可能パッケージの更新プログラム
        - C++ Build Tools コア機能
        - MSVC v143 - VS 2022 C++ x64/x86 ビルドツール
        - MSVC v142 - VS 2019 C++ x64/x86 ビルドツール
        - Windows ユニバーサル CRT
        - Windows 10 SDK
        - Windows用 C++ CMakeツール
2. CUDA対応GPUであるかどうかを `こちら <https://developer.nvidia.com/cuda-gpus>`__ で確認します。
3. CUDA Toolkitを `公式サイト <https://developer.nvidia.com/cuda-toolkit-archive>`__ からダウンロードしてからインストールします。
    1. ダウンロードするpyTorchやmmcv、onnxruntimeに、かなり複雑に依存しています。
    2. pyTorchとCUDAバージョンの関係は `こちら <https://pytorch.org/get-started/locally/>`__ で確認してください。
    3. onnxruntimeとCUDAバージョンの関係は `こちら <https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements>`__ で確認してください。
    4. Windowsの場合、システム環境変数に `CUDA_PATH` が設定されていることを確認します。cuDNNインストールで使用するので、設定されているパスをメモしておいてください。
4. 下記のコマンドでGPUドライバとCUDA Toolkitのバージョンを確認します。

    .. code-block:: bash

        $ nvidia-smi

5. cuDNNを `公式サイト <https://developer.nvidia.com/rdp/cudnn-archive>`__ からダウンロードします。
    1. cuDNNとCUDAのバージョンの関係は `こちら <https://docs.nvidia.com/deeplearning/cudnn/support-matrix/index.html>`__ で確認してください。
6. cuDNNをインストールします。
    1. Windowsの場合、zipファイルなのでファイルを解凍します。
    2. 解凍したファイルには、 `bin` 、 `include` 、 `lib` の3つのフォルダがあります。
    3. 3つのフォルダをCUDA Toolkitのインストールディレクトリ（ `CUDA_PATH`` に設定されていたパス）の中にコピーします。
    4. `bin` フォルダの中に `cudnn64_XXX.dll` （ `XXX` はバージョン）ファイルがあることを確認して、次のコマンドでエラーにならないことを確認します。

        .. code-block:: bat

            where cudnn64_XXX.dll

7. Windwosの場合 `Could not locate zlibwapi.dll. Please make sure it is in your library path!` というエラーが出る場合は、以下の手順を行ってください。
    1. `C:\Program Files\NVIDIA Corporation\Nsight System 2022.4.2\host-windows-x64\` フォルダ又は類似のフォルダにある `zlib.dll` ファイルを `%CUDA_PATH%\bin\` フォルダにコピーします。
    2. コピーした `zlib.dll` ファイルを `zlibwapi.dll` に名前を変更します。


GPU対応版のフレームワークインストール
==============================================

- mmdetectionのGPU対応版をインストールする場合、下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c mmdet --install_use_gpu

- mmpretrainのGPU対応版をインストールする場合、下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c mmpretrain --install_use_gpu

- mmclsのGPU対応版をインストールする場合、下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c mmcls --install_use_gpu

- insightfaceのGPU対応版をインストールする場合、下記のコマンドでインストールできます。
    
    .. code-block:: bash

        $ iinfer -m install -c insightface --install_use_gpu

- onnxruntimeのGPU対応版をインストールする場合、下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c onnx --install_use_gpu

GPU対応版のサーバーインストール
==============================================

- 下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c server --install_use_gpu
