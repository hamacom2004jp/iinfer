.. -*- coding: utf-8 -*-

******************
よくあるエラー
******************

エラーの原因と対処法を記載します。

.. csv-table::

    :header: "Operation","Message","Cause","How to"
    "`pip install iinfer` ","ERROR: Command errored out with exit status 1: ....  error: invalid command 'bdist_wheel' ","pipのバージョンが古い","`pip install --upgrade pip` でpipをアップデート"
    "`iinfer -m install -c mmdet` ","shutil.Error ...","現在のディレクトリにmmdetectionが既に存在したり、データフォルダ「~/.iinfer/」にmmdetectionが存在する","mmdetectionのディレクトリを削除"
    "`iinfer -m install -c mmdet` ","error: Microsoft Visual C++ 14.0 or greater is required. Get it with `Microsoft C++ Build Tools`: https://visualstudio.microsoft.com/visual-cpp-build-tools/","Windows SDKが必要です。","`Windows SDK <https://developer.microsoft.com/en-gb/windows/downloads/sdk-archive/>`__ をインストールしてください。"
    "`iinfer -m install -c mmpretrain` ","shutil.Error ...","現在のディレクトリにmmpretrainが既に存在したり、データフォルダ「~/.iinfer/」にmmpretrainが存在する","mmpretrainのディレクトリを削除"
    "`iinfer -m install -c mmrotate` ","shutil.Error ...","現在のディレクトリにmmrotateが既に存在したり、データフォルダ「~/.iinfer/」にmmrotateが存在する","mmrotateのディレクトリを削除"
    "`iinfer -m install -c insightface` ","Could not install packages due to an OSError: [WinError 5] アクセスが拒否されました。","更新ファイルが使用中？","`pip install insightface` でインストール"
    "`iinfer -m install -c insightface` ","CreateExecutionProviderInstance CUDA_PATH is set but CUDA wasnt able to be loaded.","CUDAのバージョンとonnxruntimeのバージョンが合っていない","https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html#requirements で確認し適切なバージョンのonnxruntime及びonnxruntime-guiをインストールしてください。"
    "`iinfer -m install -c insightface` ","CreateExecutionProviderInstance CUDA_PATH is set but CUDA wasnt able to be loaded.","cudnnがインストールされていない","https://developer.nvidia.com/rdp/cudnn-archive で適切なバージョンのcudnnをダウンロードしインストールしてください。"
    "`iinfer -m install -c <mm系>` ","Failed to uninstall mmcv","mmdet又はmmpretrainのモデルが起動中","`iinfer -m server` で起動したサーバープロセスを停止"
    "`iinfer -m install -c <mm系>` ","fatal: unable to access 'https://github.com/open-mmlab/mmpretrain.git/': Could not resolve host: github.com","`ping github.com` コマンドなどで名前解決できるか確認。できたら `iinfer -m install -c <mm系>` を再実行"
    "`iinfer -m client -c deploy` ","Failed to git clone mmpretrain.","gitコマンドがインストールされていません","https://git-scm.com/downloads を参照しサーバー側にgitコマンドをインストールしてください"
    "`iinfer -m client -c deploy` ","Failed to git clone mmdetection.","gitコマンドがインストールされていません","https://git-scm.com/downloads を参照しサーバー側にgitコマンドをインストールしてください"
    "`iinfer -m client -c deploy` ","Failed to git clone mmrotate.","gitコマンドがインストールされていません","https://git-scm.com/downloads を参照しサーバー側にgitコマンドをインストールしてください"
    "`iinfer -m client -c start` ","Failed to create session: No module named 'mmdet'","mmdetがインストールされていません","`iinfer -m install -c mmdet` "
    "`iinfer -m client -c start` ","Failed to create session: No module named 'mmpretrain'","mmpretrainがインストールされていません","`iinfer -m install -c mmpretrain` "
    "`iinfer -m client -c start` ","Failed to create session: No module named 'mmrotate'","mmrotateがインストールされていません","`iinfer -m install -c mmrotate` "
    "`iinfer -m client -c start` ","AssertionError: test_cfg specified in both outer field and model field","`mmdet` と `mmrotate` のバージョンの互換性がありません","両方使用する場合は `iinfer -m install -c server --install_mmrotate --install_tag mmrotate` のように別のイメージを作成してください"
    "`iinfer -m client -c predict` ","Failed to run inference: riroi_align_rotated_forward_impl: implementation for device cpu not found.","`mmrotate` を使用するときはGPUが使用できるPCが必要です","GPUが使用できるPCで実行"
    "`iinfer -m client -c predict` ","The function is not implemented. Rebuild the library with Windows, GTK+ 2.x or Cocoa support. If you are on Ubuntu or Debian, install libgtk2.0-dev and pkg-config, then re-run cmake or configure script in function 'cvShowImage'","ライブラリが不足しています","`pip uninstall -y opencv-python` で一度削除してから `pip install opencv-python` で再インストール"
    "`iinfer -m client -c predict` ","Failed to run inference: LoadAnnotations.__init__() got an unexpected keyword argument 'with_bbox'","mmdetとmmsegを一つのサーバーで同時に起動するとエラーが発生します","mmsegとmmsegの両方起動させる場合は、異なるsvnameでそれそれ別のサーバーを起動させてください"
    "`iinfer -m gui -c start` ","ModuleNotFoundError: No module named 'bottle.ext.websocket'","bottleモジュールの不具合です。python3.12以上だと発生します。","python3.11以下を使用してください。"
