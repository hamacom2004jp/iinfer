.. -*- coding: utf-8 -*-

******************
よくあるエラー
******************

エラーの原因と対処法を記載します。

.. csv-table::

    :header: "Operation","Message","Cause","How to"
    "`iinfer -m install -c mmdet` ","shutil.Error ...","現在のディレクトリにmmdetectionが既に存在したり、データディレクトリ「~/.iinfer/」にmmdetectionが存在する","mmdetectionのディレクトリを削除"
    "`iinfer -m install -c mmpretrain` ","shutil.Error ...","現在のディレクトリにmmpretrainが既に存在したり、データディレクトリ「~/.iinfer/」にmmpretrainが存在する","mmpretrainのディレクトリを削除"
    "`iinfer -m install -c <mm系>` ","Failed to uninstall mmcv","mmdet又はmmpretrainのモデルが起動中","`iinfer -m server` で起動したサーバープロセスを停止"
    "`iinfer -m client -c start -n <model_name>` ","Failed to create session: No module named 'mmdet'","mmdetがインストールされていません","`iinfer -m install -c mmdet` "
    "`iinfer -m client -c start -n <model_name>` ","Failed to create session: No module named 'mmpretrain'","mmpretrainがインストールされていません","`iinfer -m install -c mmpretrain` "
