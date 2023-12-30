.. -*- coding: utf-8 -*-

****************
開発者向け情報
****************

iinferの開発環境を構築するための手順を説明します。

プロジェクトのインストール方法
==============================

プロジェクトをインストールするには、次の手順を実行します:

1. プロジェクトをクローンします:

    .. code-block:: bat

        git clone https://github.com/hamacom2004jp/iinfer.git

2. プロジェクトのディレクトリに移動します:

    .. code-block:: bat

        cd iinfer

3. プロジェクトの仮想環境を作成します:

    .. code-block:: bat

        python -m venv .venv
        .venv\Scripts\activate

4. プロジェクトの依存関係をインストールします:

    .. code-block:: bat

        python.exe -m pip install --upgrade pip
        pip install -r requirements.txt

5. プロジェクトをビルドします:

    .. code-block:: bat

        sphinx-apidoc -F -o docs_src/resources iinfer
        sphinx-build -b html docs_src docs
        python setup.py sdist
        python setup.py bdist_wheel


モジュールのコミット方法
=========================

開発を協力いただける方は、以下のガイドラインに従ってください:

1. 新しいブランチを作成してください:

    .. code-block:: bat

        git checkout -b feature/your-feature

2. 変更を加えてコミットしてください:

    .. code-block:: bat

        git commit -m "Add your changes"

3. 作成したブランチにプッシュしてください:

    .. code-block:: bat

        git push origin feature/your-feature

4. プルリクエストを作成してください.


【参考】WSL2上にdocker導入する方法
==================================

WSL2上にdockerを導入する手順を説明します。

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

        wsl -u ubuntu -d Ubuntu_docker-20.04


【参考】pyplにアップするための手順
==================================

1. pypiのユーザー登録

   - pyplのユーザー登録【本番】
     https://pypi.org/account/register/

   - pyplのユーザー登録【テスト】
     https://test.pypi.org/account/register/

2. それぞれ2要素認証とAPIトークンを登録

3. ホームディレクトリに **.pypirc** を作成

    .. code-block:: ini

        [distutils]
        index-servers =
            pypi
            testpypi

        [pypi]
        repository: https://upload.pypi.org/legacy/
        username: __token__
        password: 本番環境のAPIトークン

        [testpypi]
        repository: https://test.pypi.org/legacy/
        username: __token__
        password: テスト環境のAPIトークン

4. テスト環境にアップロード

    .. code-block:: bat

        twine upload --repository testpypi dist/*

5. テスト環境のモジュールをインストール

    .. code-block:: bat

        pip install -i https://test.pypi.org/simple/ your-package

6. 本番環境にアップロード

    .. code-block:: bat

        twine upload --repository pypi dist/*

7. 本番環境のモジュールをインストール

    .. code-block:: bat

        pip install your-package

