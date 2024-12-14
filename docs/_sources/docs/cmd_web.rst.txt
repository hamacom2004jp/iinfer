.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（webモード）
****************************************************

- Webモードのコマンド一覧です。

Webサービス起動 : `iinfer -m web -c start <Option>`
==============================================================================

- `cmdboxのwebモードのstartコマンドオプション <https://hamacom2004jp.github.io/iinfer/docs/cmd_web.html#web-iinfer-m-web-c-start-option/>`_ に加えて下記のオプションが指定できます。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--anno_html <annotation.htmlファイルのパス>","","`annotation.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--showimg_html <showimg.htmlファイルのパス>","","`showimg.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"
    "--webcap_html <webcap.htmlファイルのパス>","","`webcap.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。"


Webcap起動 : `iinfer -m web -c webcap <Option>`
==============================================================================

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--allow_host <接続許可するIP>","","省略した時は `0.0.0.0` を使用します。"
    "--listen_webcap_port <サービスポート>","","省略した時は `8082` を使用します。"
    "--image_type <出力する画像タイプ>","","出力する画像のタイプを指定する。指定可能な画像タイプは `bmp` , `png` , `jpeg` , `capture` "
    "--outputs_key <表示項目>","","webcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。"
    "--capture_frame_width <キャプチャーサイズ(横px)>","","キャプチャーする画像の横px。受信した画像をリサイズする。"
    "--capture_frame_height <キャプチャーサイズ(縦px)>","","キャプチャーする画像の縦px。受信した画像をリサイズする。"
    "--capture_fps <キャプチャーFPS>","","キャプチャーする画像のFPS。webcap画面側がこの間隔で送信する。"
    "--capture_count <キャプチャー回数>","","キャプチャーする回数。指定した回数受信したら終了する。"

