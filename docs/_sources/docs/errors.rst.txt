.. -*- coding: utf-8 -*-

******************
よくあるエラー
******************

エラーの原因と対処法を記載します。

.. csv-table::

    :header: "Operation","Message","Cause","How to"
    "`pip install iinfer` ","ERROR: Command errored out with exit status 1: ....  error: invalid command 'bdist_wheel' ","pipのバージョンが古い","`pip install --upgrade pip` でpipをアップデート"
    "`iinfer -m install -c mmdet` ","shutil.Error ...","現在のディレクトリにmmdetectionが既に存在したり、データディレクトリ「~/.iinfer/」にmmdetectionが存在する","mmdetectionのディレクトリを削除"
    "`iinfer -m install -c mmpretrain` ","shutil.Error ...","現在のディレクトリにmmpretrainが既に存在したり、データディレクトリ「~/.iinfer/」にmmpretrainが存在する","mmpretrainのディレクトリを削除"
    "`iinfer -m install -c mmrotate` ","shutil.Error ...","現在のディレクトリにmmrotateが既に存在したり、データディレクトリ「~/.iinfer/」にmmrotateが存在する","mmrotateのディレクトリを削除"
    "`iinfer -m install -c <mm系>` ","Failed to uninstall mmcv","mmdet又はmmpretrainのモデルが起動中","`iinfer -m server` で起動したサーバープロセスを停止"
    "`iinfer -m install -c <mm系>` ","fatal: unable to access 'https://github.com/open-mmlab/mmpretrain.git/': Could not resolve host: github.com","`ping github.com`コマンドなどで名前解決できるか確認。できたら `iinfer -m install -c <mm系>`を再実行"
    "`iinfer -m client -c start -n <model_name>` ","Failed to create session: No module named 'mmdet'","mmdetがインストールされていません","`iinfer -m install -c mmdet` "
    "`iinfer -m client -c start -n <model_name>` ","Failed to create session: No module named 'mmpretrain'","mmpretrainがインストールされていません","`iinfer -m install -c mmpretrain` "
    "`iinfer -m client -c start -n <model_name>` ","Failed to create session: No module named 'mmrotate'","mmrotateがインストールされていません","`iinfer -m install -c mmrotate` "
