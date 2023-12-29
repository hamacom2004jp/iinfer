# iinfer (Visual Prediction Application)

onnx又はmmlabフォーマットの重みファイルを実行するCLIアプリケーションです。
DockerコンテナのRedisサーバーを使用します。
Windowsの場合はWSL2上のLinuxの中にDockerがインストールされている必要があります。
Linuxの場合はホスト内にDockerがインストールされている必要があります。

サポートしているAIタスクは以下のとおりです。
- Image Classification
- Object Detection


## 動作確認OS
- `Windows 10 Pro`
- `Windows 11 Pro`
- `Ubuntu20_04`


## インストール方法

``` cmd or bash
pip install iinfer
# タブ保管を有効化したい場合（Ubuntuのみ）
eval "$(register-python-argcomplete iinfer)"
```

## iinferの実行方法
``` cmd or bash
# Redisサーバーコンテナの起動（Windowsの場合）
iinfer -m redis -c docker_run --wsl_name <WSLのディストリビューションの名前> --wsl_user <WSLのLinux内のDockerが使えるユーザー>

# Redisサーバーコンテナの起動（Linuxの場合）
iinfer -m redis -c docker_run

# 推論処理を実行するサーバープロセスの起動
iinfer -m server -c start -f

# 画像AIモデルのデプロイ
iinfer -m client -c deploy -n <任意のモデル名> --model_img_width <モデルのINPUTサイズ(横幅)> --model_img_width <モデルのINPUTサイズ(縦幅)> --model_file <モデルファイル> --predict_type <推論タイプ(後述)> --custom_predict_py <カスタム推論ファイル(後述)> -f
# predict_typeはモデルのAIタスクやアルゴリズムに合わせて指定する。指定可能なキーワードは"iinfer -m client -c predict_type_list"コマンド参照。

# デプロイされている画像AIモデルの一覧
iinfer -m client -c deploy_list -f

# 画像AIモデルを起動させて推論可能な状態に(セッションを確保)する
iinfer -m client -c start -n <モデル名> --use_track -f
# use_trackを指定するとObjectDetectionタスクの結果に対して、MOT（Multi Object Tracking）を実行しトラッキングIDを出力する。

# 推論を実行する
iinfer -m client -c predict -n <モデル名> -i <推論させる画像ファイル> -o <推論結果の画像ファイル> --output_preview -f
# output_previewを指定するとimshowで推論結果画像を表示する（GUI必要）

# カメラキャプチャー画像を元に推論を実行する
iinfer -m client -c capture | iinfer -m client -c predict -n <モデル名> --output_preview --stdin --image_type capture -f
# --stdin --image_type capture で標準入力のキャプチャー画像を推論する

# 画像AIモデルを停止させてセッションを開放
iinfer -m client -c start -n <モデル名> -f

# 画像AIモデルのアンデプロイ
iinfer -m client -c undeploy -n <モデル名> -f

# 推論処理を実行するサーバープロセスの停止
iinfer -m server -c stop -f
```

### コマンドラインオプション（共通）
|Option|Required|Description|
|------|------|------|
|-h|-|ヘルプ表示|
|-u,--useopt <オプション保存するファイル>|`-s`を指定している場合〇|オプションを保存しているファイルを使用する|
|-s,--saveopt|-|指定しているオプションを`-u`で指定したファイルに保存する|
|-f,--format|-|処理結果を見やすい形式で出力する。指定しない場合json形式で出力する。|
|--version|-|バージョン表示|

### コマンドラインオプション（初期設定） : `iinfer -m install -c <Command> <Option>`
`iinfer`をインストールした直後にはAIフレームワークのインストールがされていない状態です。
通常推論サーバー側にしかAIフレームワークが必要ないため、任意でインストールできるようにしました。
|Command|Option|Required|Description|
|------|------|------|------|
|onnx|-|-|`onnxruntime`をインストールする|
|mmdet|-|-|`mmdetection`をインストールする|
|redis|-|-|`redis-server`のdockerイメージをPULLする|
|^|--wsl_name <ディストリビューション名>|Windowsの場合は〇|Windowsの場合はWSLのディストリビューションの名前を指定する|
|^|--wsl_user <user名>|Windowsの場合は〇|Windowsの場合はWSL内のユーザー名を指定する|
|server|-|-|`推論サーバー`のdockerイメージを`build`する。<br>このコマンドで作成されるdockerイメージには、上記`onnxruntime`と`mmdetection`が含まれる。<br>`build`が成功すると`docker-compose.yml`ファイルが生成される。<br>windows環境は未サポートなので、普通に`iinfer -m server`を使ってください。|
|--data <データディレクトリ>|-|省略した時は`$HONE/.iinfer`を使用する|

### Redisサーバー起動 : `iinfer -m redis -c docker_run <Option>`
|Option|Required|Description|
|------|------|------|
|--port <ポート番号>|-|Redisサーバーのサービスポート(任意)を指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|--wsl_name <ディストリビューション名>|Windowsの場合は〇|Windowsの場合はWSLのディストリビューションの名前を指定する|
|--wsl_user <user名>|Windowsの場合は〇|Windowsの場合はWSL内のユーザー名を指定する|

### Redisサーバー停止 : `iinfer -m redis -c docker_stop <Option>`
|Option|Required|Description|
|------|------|------|
|--wsl_name <ディストリビューション名>|Windowsの場合は〇|Windowsの場合はWSLのディストリビューションの名前を指定する|
|--wsl_user <user名>|Windowsの場合は〇|Windowsの場合はWSL内のユーザー名を指定する|

### 推論サーバー起動 : `iinfer -m server -c start <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|--data <データディレクトリ>|-|省略した時は`$HONE/.iinfer`を使用する|

### 推論サーバー停止 : `iinfer -m server -c stop <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの配備) : `iinfer -m client -c deploy <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|-n,--name <登録名>|〇|AIモデルの登録名(任意)を指定する|
|--model_file <モデルファイル>|〇|学習済みのモデルファイルを指定する|
|--model_conf_file <モデル設定ファイル>|-|mmlabの場合はモデル設定ファイルを指定する。複数指定可能ですが、最初に指定したファイルが`start`時に使用されます。|
|--model_img_width <モデルのINPUTサイズ(横px)>|-|AIモデルのINPUTサイズ(横px)を指定する|
|--model_img_height <モデルのINPUTサイズ(縦px)>|-|AIモデルのINPUTサイズ(縦px)を指定する|
|--predict_type <推論タイプ>|〇|AIモデルの推論タイプを指定する。指定可能なタイプは`predict_type_list`参照|
|--custom_predict_py <カスタム推論pyファイル>|-|独自の推論タイプを作成するときに指定。この時は`--predict_type Custom`を指定|
|--label_file <ラベルファイル>|-|推論結果のクラスラベルファイルを指定。改行区切りでラベル名(行indexがクラスと一致する)を指定したファイル。|
|--color_file <色ファイル>|-|推論結果の可視化画像の色ファイルを指定。改行区切りで色(行indexがクラスと一致する)を指定したファイル。|
|--overwrite|-|デプロイ済みであっても上書きする|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの配備一覧) : `iinfer -m client -c deploy_list <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの配備解除) : `iinfer -m client -c undeploy <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの起動) : `iinfer -m client -c start <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--model_provider <モデルプロバイダー>|-|ONNX形式のモデルファイルの場合に指定可能。指定可能なプロバイダーは`CPUExecutionProvider`,`CUDAExecutionProvider`,`TensorrtExecutionProvider`|
|--use_track|-|ObjectDetectionタスクの場合に指定可能。motpyを使ってトラッキングID付与を行う|
|--gpuid <GPUのid>|-|GPUのディバイスIDを指定する。`--model_provider`でGPUを使用するプロバイダーを指定した時に使用可能|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(推論タイプ一覧) : `iinfer -m client -c predict_type_list <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|

### クライアント(AIモデルの停止) : `iinfer -m client -c stop <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(推論の実行) : `iinfer -m client -c predict <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|--password <パスワード>|-|Redisサーバーのアクセスパスワード(任意)を指定する。省略時は`password`を使用する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|-i,--input_file <推論対象の画像ファイル>|-|推論させる画像をファイルで指定する|
|--stdin|-|推論させる画像を標準入力から読み込む|
|--nodraw|-|推論結果画像にbbox等の描き込みを行わない|
|--image_type <推論対象の画像タイプ>|-|推論させる画像のタイプを指定する。指定可能な画像タイプは`bmp`, `png`, `jpeg`, `capture`|
|-o,--output_file <推論結果画像の保存先ファイル>|--stdinを指定した時〇|推論結果画像の保存先ファイルを指定する|
|-P,--output_preview|-|推論結果画像を`cv2.imshow`で表示する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(キャプチャーの実行) : `iinfer -m client -c capture <Option>`
このコマンドは、パイプで接続して下記のように使用します。
``` cmd or bash
iinfer -m client -c capture <Option> | iinfer -m client -c predict --stdin --image_type capture <Option>
```
|Option|Required|Description|
|------|------|------|
|--capture_device <ディバイス>|-|キャプチャーディバイスを指定する。`cv2.VideoCapture`の第一引数に渡される値。|
|--capture_frame_width <キャプチャーサイズ(横px)>|-|キャプチャーする画像の横px。`cv2.VideoCapture`オブジェクトの`cv2.CAP_PROP_FRAME_WIDTH`オプションに指定する値。|
|--capture_frame_height <キャプチャーサイズ(縦px)>|-|キャプチャーする画像の縦px。`cv2.VideoCapture`オブジェクトの`cv2.CAP_PROP_FRAME_HEIGHT`オプションに指定する値。|
|--capture_fps <キャプチャーFPS>|-|キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepする|
|--capture_count <キャプチャー回数>|-|キャプチャー回数。AIの推論速度が指定した値より高速な場合に残り時間分をsleepする|
|--output_preview|-|推論結果画像を`cv2.imshow`で表示する|

### 後処理(物体検知フィルター) : `iinfer -m postprocess -c det_filter <Option>`
|Option|Required|Description|
|------|------|------|
|-i,--input_file <推論結果ファイル>|`--stdin`を指定しない場合〇|後処理させる推論結果をファイルで指定する。|
|--stdin|`--input_file`を指定しない場合〇|後処理させる推論結果を標準入力から読み込む|
|--score_th|-|bboxのクラススコアがこの値以下のものは除去されます|
|--width_th|-|bboxの横幅がこの長さ以下のものは除去されます|
|--height_th|-|bboxの縦幅がこの長さ以下のものは除去されます|
|--classes|-|このクラス以外のbboxは除去されます。複数指定できます|
|--labels|-|このラベル以外のbboxは除去されます。複数指定できます|
|--nodraw|-|推論結果画像にbbox等の描き込みを行わない|
|-P,--output_preview|-|推論結果画像を`cv2.imshow`で表示する|

### 後処理(物体検知判定) : `iinfer -m postprocess -c det_jadge <Option>`
|Option|Required|Description|
|------|------|------|
|-i,--input_file <推論結果ファイル>|`--stdin`を指定しない場合〇|後処理させる推論結果をファイルで指定する。|
|--stdin|`--input_file`を指定しない場合〇|後処理させる推論結果を標準入力から読み込む|
|--ok_score_th|-|クラススコアがこの値以上のものはok判定されます|
|--ok_classes|`ok_score_th`を指定する場合は`ok_classes`か`ok_labels`が〇|okクラスに含めるクラスindexを指定します。複数指定できます。|
|--ok_labels|`ok_score_th`を指定する場合は`ok_classes`か`ok_labels`が〇|okクラスに含めるクラスラベルを指定します。複数指定できます。|
|--ng_score_th|-|クラススコアがこの値以上のものはng判定されます|
|--ng_classes|`ng_score_th`を指定する場合は`ng_classes`か`ng_labels`が〇|ngクラスに含めるクラスindexを指定します。複数指定できます。|
|--ng_labels|`ng_score_th`を指定する場合は`ng_classes`か`ng_labels`が〇|ngクラスに含めるクラスラベルを指定します。複数指定できます。|
|--ext_score_th|-|クラススコアがこの値以上のものはgray判定されます|
|--ext_classes|`ng_score_th`を指定する場合は`ext_classes`か`ext_labels`が〇|grayクラスに含めるクラスindexを指定します。複数指定できます。|
|--ext_labels|`ng_score_th`を指定する場合は`ext_classes`か`ext_labels`が〇|grayクラスに含めるクラスラベルを指定します。複数指定できます。|
|--nodraw|-|推論結果画像にbbox等の描き込みを行わない|
|-P,--output_preview|-|推論結果画像を`cv2.imshow`で表示する|

### 後処理(画像分類判定) : `iinfer -m postprocess -c cls_jadge <Option>`
|Option|Required|Description|
|------|------|------|
|-i,--input_file <推論結果ファイル>|`--stdin`を指定しない場合〇|後処理させる推論結果をファイルで指定する。|
|--stdin|`--input_file`を指定しない場合〇|後処理させる推論結果を標準入力から読み込む|
|--ok_score_th|-|クラススコアがこの値以上のものはok判定されます|
|--ok_classes|`ok_score_th`を指定する場合は`ok_classes`か`ok_labels`が〇|okクラスに含めるクラスindexを指定します。複数指定できます。|
|--ok_labels|`ok_score_th`を指定する場合は`ok_classes`か`ok_labels`が〇|okクラスに含めるクラスラベルを指定します。複数指定できます。|
|--ng_score_th|-|クラススコアがこの値以上のものはng判定されます|
|--ng_classes|`ng_score_th`を指定する場合は`ng_classes`か`ng_labels`が〇|ngクラスに含めるクラスindexを指定します。複数指定できます。|
|--ng_labels|`ng_score_th`を指定する場合は`ng_classes`か`ng_labels`が〇|ngクラスに含めるクラスラベルを指定します。複数指定できます。|
|--ext_score_th|-|クラススコアがこの値以上のものはgray判定されます|
|--ext_classes|`ng_score_th`を指定する場合は`ext_classes`か`ext_labels`が〇|grayクラスに含めるクラスindexを指定します。複数指定できます。|
|--ext_labels|`ng_score_th`を指定する場合は`ext_classes`か`ext_labels`が〇|grayクラスに含めるクラスラベルを指定します。複数指定できます。|
|--nodraw|-|推論結果画像にbbox等の描き込みを行わない|
|-P,--output_preview|-|推論結果画像を`cv2.imshow`で表示する|

### 後処理(CSV出力) : `iinfer -m postprocess -c csv <Option>`
|Option|Required|Description|
|------|------|------|
|-i,--input_file <推論結果ファイル>|`--stdin`を指定しない場合〇|後処理させる推論結果をファイルで指定する。|
|--stdin|`--input_file`を指定しない場合〇|後処理させる推論結果を標準入力から読み込む|
|--out_headers|-|出力するヘッダーを指定します。複数指定できます。|
|--noheader|-|ヘッダー行の出力を行わない|
|-f,--format|-|このコマンドではこのオプションは無視されます。|

### 後処理(HTTPリクエストの実行) : `iinfer -m postprocess -c httpreq <Option>`
|Option|Required|Description|
|------|------|------|
|-i,--input_file <推論結果ファイル>|`--stdin`を指定しない場合〇|後処理させる推論結果をファイルで指定する。|
|--stdin|`--input_file`を指定しない場合〇|後処理させる推論結果を標準入力から読み込む|
|--json_connectstr <URL>|〇|推論結果のJSONのPOST先URLを指定する|
|--img_connectstr <URL>|-|推論結果の画像のPOST先URLを指定する|
|--fileup_name <パラメータ名>|-|推論結果の画像をPOSTするときのパラメータ名を指定する。省略すると`file`が使用される。|

### よくあるエラー
|Operation|Message|Cause|How to|
|------|------|------|------|
|`iinfer -m install -c mmdet`|shutil.Error ...|現在のディレクトリにmmdetectionが既に存在したり、データディレクトリ「~/.iinfer/」にmmdetectionが存在する|mmdetectionのディレクトリを削除|
|`iinfer -m install -c mmpretrain`|shutil.Error ...|現在のディレクトリにmmpretrainが既に存在したり、データディレクトリ「~/.iinfer/」にmmpretrainが存在する|mmpretrainのディレクトリを削除|
|`iinfer -m install -c <mm系>`|Failed to uninstall mmcv|mmdet又はmmpretrainのモデルが起動中|`iinfer -m server`で起動したサーバープロセスを停止|
|`iinfer -m client -c start -n <model_name>`|Failed to create session: No module named 'mmdet'|mmdetがインストールされていません|`iinfer -m install -c mmdet`|
|`iinfer -m client -c start -n <model_name>`|Failed to create session: No module named 'mmpretrain'|mmpretrainがインストールされていません|`iinfer -m install -c mmpretrain`|


## カスタム推論モジュールについて
AIモデルの配備`iinfer -m client -c deploy <Option>`コマンドで`--predict_type Custom`且つ`--custom_predict_py <カスタム推論pyファイル>`オプションを指定すると、カスタムモデルを配備できます。
カスタム推論pyファイルは`iinfer.app.predict.Predict`クラスを継承させたクラスを作成してください。
`iinfer.app.predict.Predict`クラスの定義は下記の通りで、継承したクラスは`create_session`と`predict`メソッドを定義してください。

``` python
from pathlib import Path
from PIL import Image
from typing import List, Tuple, Dict, Any
import logging

class Predict(object):
    def create_session(self, logger:logging.Logger, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None) -> Any:
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードを行い、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            logger (logging.Logger): ロガー
            model_path (Path): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            推論セッション
        """
        raise NotImplementedError()

    def predict(self, session, img_width:int, img_height:int, image:Image, labels:List[str]=None, colors:List[Tuple[int]]=None, nodraw:bool=False) -> Tuple[Dict[str, Any], Image.Image]:
        """
        予測を行う関数です。
        predictコマンドやcaptureコマンド実行時に呼び出されます。
        引数のimageはRGBですので、戻り値の出力画像もRGBにしてください。
        戻り値の推論結果のdictは、通常推論結果項目ごとに値(list)を設定します。
        例）Image Classification（EfficientNet_Lite4）の場合
        return dict(output_scores=output_scores, output_classes=output_classes), image_obj
        例）Object Detection（YoloX）の場合
        return dict(output_boxes=final_boxes, output_scores=final_scores, output_classes=final_cls_inds), output_image

        Args:
            session: 推論セッション
            img_width (int): モデルのINPUTサイズ（画像の幅）
            img_height (int): モデルのINPUTサイズ（画像の高さ）
            image (Image): 入力画像（RGB配列であること）
            labels (List[str], optional): クラスラベルのリスト. Defaults to None.
            colors (List[Tuple[int]], optional): ボックスの色のリスト. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.

        Returns:
            Tuple[Dict[str, Any], Image]: 予測結果と出力画像(RGB)のタプル
        """
        raise NotImplementedError()
```

## iinferコマンドについて
```python -m iinfer```の省略形です。
実体は```scripts```ディレクトリ内にあります。

### データの保存場所
```
pathlib.Path(HOME_DIR) / '.iinfer'
```

## 動作確認したモデル
|AI Task|base|frameWork|input|model|predict_type|memo|
|------|------|------|------|------|------|------|
|Object Detection|[YOLOX](https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox)|mmdetection|416x416|YOLOX-tiny|mmdet_det_YoloX_Lite|-|
|Object Detection|[YOLOX](https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox)|mmdetection|640x640|YOLOX-s|mmdet_det_YoloX|-|
|Object Detection|[YOLOX](https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox)|mmdetection|640x640|YOLOX-l|mmdet_det_YoloX|-|
|Object Detection|[YOLOX](https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox)|mmdetection|640x640|YOLOX-x|mmdet_det_YoloX|-|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|416x416|YOLOX-Nano|onnx_det_YoloX_Lite|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|416x416|YOLOX-Tiny|onnx_det_YoloX_Lite|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-s|onnx_det_YoloX|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-m|onnx_det_YoloX|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-l|onnx_det_YoloX|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-x|onnx_det_YoloX|*1|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-10|onnx_det_YoloV3|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-12|onnx_det_YoloV3|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-12-int8|onnx_det_YoloV3|-|
|Object Detection|[TinyYOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3)|onnx|416x416|TinyYOLOv3|onnx_det_TinyYoloV3|-|
|Image Classification|[Swin Transformer](https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer)|mmpretrain|224x224|swin-tiny_16xb64_in1k|mmpretrain_cls_swin_Lite|-|
|Image Classification|[Swin Transformer](https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer)|mmpretrain|224x224|swin-small_16xb64_in1k|mmpretrain_cls_swin_Lite|-|
|Image Classification|[Swin Transformer](https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer)|mmpretrain|384x384|swin-base_16xb64_in1k-384px|mmpretrain_cls_swin|-|
|Image Classification|[Swin Transformer](https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer)|mmpretrain|384x384|swin-large_16xb64_in1k-384px|mmpretrain_cls_swin|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11|onnx_cls_EfficientNet_Lite4|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11-int8|onnx_cls_EfficientNet_Lite4|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11-qdq|onnx_cls_EfficientNet_Lite4|-|

*1）[pth2onnx](https://github.com/hamacom2004jp/pth2onnx)を使用してONNX形式に変換して使用

## 開発環境構築
```
git clone https://github.com/hamacom2004jp/iinfer.git
cd iinfer
python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

#### WSL2上にredis-serverのdocker導入
```
# Ubuntuイメージインストール（cmdプロンプトで実行：ubuntuユーザーを作成する）
wsl --install -d Ubuntu-20.04

# Ubuntu初期設定（bash上で実行）
cd /etc/apt
sudo sed -i.bak -e "s/http:\/\/archive\.ubuntu\.com/http:\/\/jp\.archive\.ubuntu\.com/g" sources.list
sudo apt update
sudo apt install -y language-pack-ja manpages-ja manpages-ja-dev
sudo update-locale LANG=ja_JP.UTF-8

# Dockerインストール（bash上で実行）
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
cd ~/
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install -y docker-ce docker-compose
sudo usermod -aG docker ubuntu
exit

# Ubuntuイメージ再起動（cmdプロンプトで実行）
wsl --shutdown
wsl --export Ubuntu-20.04 Ubuntu_wsl2_docker-20.04.tar
wsl --unregister Ubuntu-20.04
mkdir Ubuntu_docker-20.04
wsl --import Ubuntu_docker-20.04 Ubuntu_docker-20.04 Ubuntu_wsl2_docker-20.04.tar --version 2
wsl -u ubuntu -d Ubuntu_docker-20.04

# redis-server起動
docker run -d --name redis-container --rm -e TZ=UTC -p 6379:6379 -e REDIS_PASSWORD=<password> ubuntu/redis:latest

```

## pyplにアップするための準備

``` cmd or bash
python setup.py sdist
python setup.py bdist_wheel
```

- pyplのユーザー登録【本番】
  https://pypi.org/account/register/

- pyplのユーザー登録【テスト】
  https://test.pypi.org/account/register/

- それぞれ2要素認証とAPIトークンを登録

- ホームディレクトリに```.pypirc```を作成
``` .pypirc
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
```

- テスト環境にアップロード
  ```.pyplrc```を作っていない場合はコマンド実行時にusernameとpasswordを要求される
  成功するとURLが返ってくる。
``` cmd or bash
twine upload --repository testpypi dist/*
```
- pipコマンドのテスト
``` cmd or bash
pip install -i https://test.pypi.org/simple/ iinfer
```

- 本番環境にアップロード
``` cmd or bash
twine upload --repository pypi dist/*
```

## Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
