.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（guiモード）
****************************************************

- GUIモードのコマンド一覧です。

管理画面起動 : `iinfer -m gui -c start <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します"
    "--svname <推論サービス名>","","推論サーバーのサービス名を指定します。省略時は `server` を使用します"
    "--data <データフォルダ>","","省略した時は `$HONE/.iinfer` を使用します。"
    "--allow_host <接続許可するIP>","","省略した時は `0.0.0.0` を使用します。"
    "--listen_port <サービスポート>","","省略した時は `8081` を使用します。"
    "--signin_file <ユーザーリストファイル>","","ログイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。ログインファイルは、各行が1ユーザーを示し、ユーザーID、パスワード、ハッシュアルゴリズム名の順で、「 : 」で区切って記載します。ハッシュアルゴリズム名は「plain」「md5」「sha1」「sha256」が指定できます。"
    "--client_only","","iinferサーバーへの接続を行わないようにします。"
    "--gui_html <gui.htmlファイルのパス>","","`gui.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--filer_html <filer.htmlファイルのパス>","","`filer.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--showimg_html <showimg.htmlファイルのパス>","","`showimg.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--webcap_html <webcap.htmlファイルのパス>","","`webcap.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--assets <jsやcssファイルのパス>","","htmlファイルを使用する場合に必要なアセットファイルを指定します。"
    "--signin_html <signin.htmlファイルのパス>","","`signin.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"

