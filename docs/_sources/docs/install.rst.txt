.. -*- coding: utf-8 -*-

****************************************************
インストール
****************************************************

- `iinfer` はクライアントとサーバーの両方の環境を構築する必要があります。
- もちろん１台のPCで両方の環境を構築することも可能です。
    - :ref:`クライアント環境構築 <client_install>`
    - :ref:`サーバー環境構築する場合 <server_ubuntu_install>`
    - :ref:`サーバー（WSL2+Docker）環境構築する場合 <server_wsl2docker_install>`
    - :ref:`サーバー（GPU）環境構築する場合 <server_gpu_install>`
- なおサーバー環境の動作確認状況は下記のとおりです。

.. csv-table::

    "","Ubuntu（Host）","Ubuntu（Docker）","Windows（Host）","Windows（WSL2+Docker）"
    "CPU","確認済","確認済","確認済","確認済"
    "GPU","<多分動く>","<多分動く>","確認済","確認済"

.. _client_install:

クライアント環境構築
======================

- まず最初に `iinfer` をインストールします。
- `iinfer` はPython3.8以上で動作します。
- これがクライアントとして動作します。

１．`iinfer` のインストール
--------------------------------

- Windowsの場合

    .. code-block:: bat

        python3 -m venv .venv
        .venv\\Scripts\\activate
        pip install --upgrade pip
        pip install iinfer

- Ubuntuの場合

    .. code-block:: bash

        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install iinfer
        eval "$(register-python-argcomplete iinfer)"


.. _server_ubuntu_install:

サーバー（Ubuntu）環境構築する場合
====================================

- `iinfer` を使用して各種AIフレームワークをインストールしたDockerイメージを構築することが出来ます。
- 物体検知を実行するための手順を解説します。

１．Dockerイメージを構築
-----------------------------

- `iinfer -m install -c server <Option>` コマンドで推論サーバーを構築できます。
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
----------------------------------------------------

- `iinfer -m client -c deploy_list <Option>` コマンドで推論サーバー接続を試してみます。
- `--svname server_mmdet` コマンドで推論サーバー名を指定しています。

    .. code-block:: bash

         $ iinfer -m client -c deploy_list --svname server_mmdet


.. _server_wsl2docker_install:

サーバー（WSL2+Docker）環境構築する場合
=========================================

- Windows環境ではWSL2を使用してUbuntu環境を構築することが出来ます。
- 以下の手順で推論サーバーを構築してみます。

1. Ubuntuイメージインストール（cmdプロンプトで実行 : ubuntuユーザーを作成する）

    .. code-block:: bat

        wsl --install -d Ubuntu-20.04

2. Ubuntu初期設定（bash上で実行）

    .. code-block:: bash

        cd /etc/apt
        sudo sed -i.bak -e "s/http:\/\/archive\.ubuntu\.com/http:\/\/jp\.archive\.ubuntu\.com/g" sources.list
        sudo apt update
        sudo apt install -y language-pack-ja manpages-ja manpages-ja-dev
        sudo update-locale LANG=ja_JP.UTF-8

3. Dockerインストール（bash上で実行）

    .. code-block:: bash

        sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
        cd ~/
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
        sudo apt update
        apt-cache policy docker-ce
        sudo apt install -y docker-ce docker-compose
        sudo usermod -aG docker ubuntu
        exit

4. Dockerインストール済みWSL2イメージ生成（cmdプロンプトで実行）

    .. code-block:: bat

        wsl --shutdown
        wsl --export Ubuntu-20.04 Ubuntu_wsl2_docker-20.04.tar
        wsl --unregister Ubuntu-20.04
        mkdir Ubuntu_docker-20.04
        wsl --import Ubuntu_docker-20.04 Ubuntu_docker-20.04 Ubuntu_wsl2_docker-20.04.tar --version 2

5. Dockerインストール済みWSL2イメージ生成（cmdプロンプトで実行）

    .. code-block:: bat

        wsl -d Ubuntu_docker-20.04 -u ubuntu


.. _server_gpu_install:

サーバー（GPU）環境構築する場合
=================================

- サーバー環境にGPUを搭載した場合、GPU環境を構築することが出来ます。
- なおこの手順はNVIDIA製のGPUを使用する場合の手順です。

１．CUDA + cuDNNのインストール
--------------------------------

1. Windowsの場合 `Build Tools for Visual Studio 2022 <https://visualstudio.microsoft.com/ja/visual-cpp-build-tools/>`__ をインストールします。
    1. インストールするモジュールは以下の通りです。環境によって必要なものが異なる場合があります。
        - C++ 2022 再配布可能パッケージの更新プログラム
        - C++ Build Tools コア機能
        - MSVC v143 - VS 2022 C++ x64/x86 ビルドツール
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
        $ /usr/local/cuda/bin/nvcc --version

5. cuDNNを `公式サイト <https://developer.nvidia.com/rdp/cudnn-archive>`__ からダウンロードします。
    1. cuDNNとCUDAのバージョンの関係は `こちら <https://docs.nvidia.com/deeplearning/cudnn/support-matrix/index.html>`__ で確認してください。
6. cuDNNをインストールします。
    1. Windowsの場合、zipファイルなのでファイルを解凍します。
    2. Windowsの場合、解凍したファイルには、 `bin` 、 `include` 、 `lib` の3つのフォルダがあります。
    3. Windowsの場合、3つのフォルダをCUDA Toolkitのインストールディレクトリ（ `CUDA_PATH`` に設定されていたパス）の中にコピーします。
    4. Windowsの場合、`bin` フォルダの中に `cudnn64_XXX.dll` （ `XXX` はバージョン）ファイルがあることを確認して、次のコマンドでエラーにならないことを確認します。

        .. code-block:: bat

            where cudnn64_XXX.dll

7. Windwosの場合 `Could not locate zlibwapi.dll. Please make sure it is in your library path!` というエラーが出る場合は、以下の手順を行ってください。
    1. `C:\Program Files\NVIDIA Corporation\Nsight System 2022.4.2\host-windows-x64\` フォルダ又は類似のフォルダにある `zlib.dll` ファイルを `%CUDA_PATH%\bin\ ` フォルダにコピーします。
    2. コピーした `zlib.dll` ファイルを `zlibwapi.dll` に名前を変更します。

8. Dockerを使用する( `iinfer -m install -c server` コマンドを使用する )場合、docker-composeのバージョンを1.28以降にします。

    1. docker-composeのバージョンを確認します。

        .. code-block:: bash

            docker-compose --version

    2. docker-composeのバージョンが1.28以降でない場合、以下のコマンドでバージョンをアップデートします。

        .. code-block:: bash

            sudo rm -rf /usr/bin/docker-compose
            sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

9. Dockerを使用する( `iinfer -m install -c server` コマンドを使用する )場合、NVIDIA Container Toolkitをインストールします。

    .. code-block:: bash
            
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
            && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
            && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
        sudo apt-get update
        sudo apt-get install -y nvidia-container-toolkit
        sudo nvidia-ctk runtime configure --runtime=docker

    ここでUbuntuの再起動を行うこと。

２．GPU対応版のサーバーインストール
----------------------------------------

- 下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c server --install_use_gpu

３．GPU対応版のフレームワークインストール
--------------------------------------------

- Dockerを使用せずに、GPU対応版のフレームワークをインストールする場合、下記のコマンドでインストールできます。

    .. code-block:: bash

         $ iinfer -m install -c mmdet --install_use_gpu
         $ iinfer -m install -c mmpretrain --install_use_gpu
         $ iinfer -m install -c mmcls --install_use_gpu
         $ iinfer -m install -c insightface --install_use_gpu
         $ iinfer -m install -c onnx --install_use_gpu
