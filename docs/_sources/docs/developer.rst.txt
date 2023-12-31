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

