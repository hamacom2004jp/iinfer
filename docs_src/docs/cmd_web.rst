.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（webモード）
****************************************************

- Webモードのコマンド一覧です。

Webサービス起動 : `iinfer -m web -c start <Option>`
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
    "--client_only","","iinferサーバーへの接続を行わないようにします。"
    "--outputs_key <表示項目>","","showimg及びwebcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。"
    "--filer_html <filer.htmlファイルのパス>","","`filer.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--showimg_html <showimg.htmlファイルのパス>","","`showimg.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--webcap_html <webcap.htmlファイルのパス>","","`webcap.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--assets <jsやcssファイルのパス>","","htmlファイルを使用する場合に必要なアセットファイルを指定します。"


Webサービス停止 : `iinfer -m web -c stop <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <データフォルダ>","","省略した時は `$HONE/.iinfer` を使用します。"


Webcap起動 : `iinfer -m web -c webcap <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--allow_host <接続許可するIP>","","省略した時は `0.0.0.0` を使用します。"
    "--listen_port <サービスポート>","","省略した時は `8082` を使用します。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--outputs_key <表示項目>","","webcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。"
    "--capture_frame_width <キャプチャーサイズ(横px)>","","キャプチャーする画像の横px。受信した画像をリサイズする。"
    "--capture_frame_height <キャプチャーサイズ(縦px)>","","キャプチャーする画像の縦px。受信した画像をリサイズする。"
    "--capture_fps <キャプチャーFPS>","","キャプチャーする画像のFPS。webcap画面側がこの間隔で送信する。"
    "--capture_count <キャプチャー回数>","","キャプチャーする回数。指定した回数受信したら終了する。"
    "--access_url <webcapのURL>","","クライアントからアクセスするときのURL。省略した時は `webcap/pub_img` を使用します。例えば `http://localhost:<listen_port>/webcap/pub_img` を指定します。"
