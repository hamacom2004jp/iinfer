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
```

## iinferの実行方法
``` cmd or bash
# Redisサーバーコンテナの起動（Windowsの場合）
iinfer -p <任意のPW> -m redis -c docker_run --wsl_name <WSLのディストリビューションの名前> --wsl_user <WSLのLinux内のDockerが使えるユーザー>

# Redisサーバーコンテナの起動（Linuxの場合）
iinfer -p <任意のPW> -m redis -c docker_run

# 推論処理を実行するサーバープロセスの起動
iinfer -p <PW> -m server -f

# 画像AIモデルのデプロイ
iinfer -p <PW> -m client -c deploy -n <任意のモデル名> --model_img_width <モデルのINPUTサイズ(横幅)> --model_img_width <モデルのINPUTサイズ(縦幅)> --model_onnx <モデルファイル> --predict_type <推論タイプ(後述)> --custom_predict_py <カスタム推論ファイル(後述)> -f
# predict_typeはモデルのAIタスクやアルゴリズムに合わせて指定する。指定可能なキーワードはヘルプ参照。

# デプロイされている画像AIモデルの一覧
iinfer -p <PW> -m client -c deploy_list -f

# 画像AIモデルを起動させて推論可能な状態に(セッションを確保)する
iinfer -p <PW> -m client -c start -n <モデル名> --model_provider <推論プロバイダー名(後述)> --use_track -f
# model_providerは推論で使用する実行環境を指定する。指定可能なキーワードはヘルプ参照。
# use_trackを指定するとObjectDetectionタスクの結果に対して、MOT（Multi Object Tracking）を実行しトラッキングIDを出力する。

# 推論を実行する
iinfer -p <PW> -m client -c predict -n <モデル名> -i <推論させる画像ファイル> -o <推論結果の画像ファイル> --output_preview -f
# output_previewを指定するとimshowで推論結果画像を表示する（GUI必要）

# 画像AIモデルを停止させてセッションを開放
iinfer -p <PW> -m client -c start -n <モデル名> -f

# 画像AIモデルのアンデプロイ
iinfer -p <PW> -m client -c undeploy -n <モデル名> -f
```

### コマンドラインオプション（共通）
|Option|Required|Description|
|------|------|------|
|-h|-|ヘルプ表示|
|-u,--useopt <オプション保存するファイル>|`-s`を指定している場合〇|オプションを保存しているファイルを使用する|
|-s,--saveopt|-|指定しているオプションを`-u`で指定したファイルに保存する|
|-f,--format|-|処理結果を見やすい形式で出力する。指定しない場合json形式で出力する。|

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
|server|-|-|`推論サーバー`のdockerイメージを`build`する<br>このコマンドで作成されるdockerイメージには、上記`onnxruntime`と`mmdetection`が含まれる<br>`build`が成功すると`docker-compose.yml`ファイルが生成される<br>windows環境は未サポートなので、普通に`iinfer -m server`を使ってください|

### Redisサーバー起動 : `iinfer -m redis -c docker_run <Option>`
|Option|Required|Description|
|------|------|------|
|--port <ポート番号>|-|Redisサーバーのサービスポート(任意)を指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワード(任意)を指定する|
|--wsl_name <ディストリビューション名>|Windowsの場合は〇|Windowsの場合はWSLのディストリビューションの名前を指定する|
|--wsl_user <user名>|Windowsの場合は〇|Windowsの場合はWSL内のユーザー名を指定する|

### Redisサーバー停止 : `iinfer -m redis -c docker_stop <Option>`
|Option|Required|Description|
|------|------|------|
|--wsl_name <ディストリビューション名>|Windowsの場合は〇|Windowsの場合はWSLのディストリビューションの名前を指定する|
|--wsl_user <user名>|Windowsの場合は〇|Windowsの場合はWSL内のユーザー名を指定する|

### 推論サーバー起動 : `iinfer -m server <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|

### クライアント(AIモデルの配備) : `iinfer -m client -c deploy <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名(任意)を指定する|
|--model_file <モデルファイル>|〇|学習済みのモデルファイルを指定する|
|--model_conf_file <モデル設定ファイル>|-|mmlabの場合はモデル設定ファイルを指定する|
|--model_img_width <モデルのINPUTサイズ(横px)>|-|AIモデルのINPUTサイズ(横px)を指定する|
|--model_img_height <モデルのINPUTサイズ(縦px)>|-|AIモデルのINPUTサイズ(縦px)を指定する|
|--predict_type <推論タイプ>|〇|AIモデルの推論タイプを指定する。指定可能なタイプは`-c predict_type_list`参照|
|--custom_predict_py <カスタム推論pyファイル>|-|独自の推論タイプを作成するときに指定。この時は`--predict_type Custom`を指定|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの配備一覧) : `iinfer -m client -c deploy_list <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの配備解除) : `iinfer -m client -c undeploy <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(AIモデルの起動) : `iinfer -m client -c start <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--model_provider <モデルプロバイダー>|-|ONNX形式のモデルファイルの場合に指定可能。指定可能なプロバイダーは`-h`参照|
|--use_track|-|ObjectDetectionタスクの場合に指定可能。motpyを使ってトラッキングID付与を行う|
|--gpuid <GPUのid>|-|GPUのディバイスIDを指定する。`--model_provider`でGPUを使用するプロバイダーを指定した時に使用可能|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(推論タイプ一覧) : `iinfer -m client -c predict_type_list <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|

### クライアント(AIモデルの停止) : `iinfer -m client -c stop <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(推論の実行) : `iinfer -m client -c predict <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|-i,--image_file <推論対象の画像ファイル>|-|推論させる画像をファイルで指定する|
|--image_stdin|-|推論させる画像を標準入力から読み込む|
|--image_type <推論対象の画像タイプ>|-|推論させる画像のタイプを指定する。指定可能な画像タイプは`-h`参照|
|-o,--output_image_file <推論結果画像の保存先ファイル>|-|推論結果画像の保存先ファイルを指定する|
|--output_preview|-|推論結果画像を`cv2.imshow`で表示する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

### クライアント(キャプチャーによる推論の実行) : `iinfer -m client -c capture <Option>`
|Option|Required|Description|
|------|------|------|
|--host <IPアドレス又はホスト名>|-|Redisサーバーのサービスホストを指定する|
|--port <ポート番号>|-|Redisサーバーのサービスポートを指定する|
|-p,--password <パスワード>|〇|Redisサーバーのアクセスパスワードを指定する|
|-n,--name <登録名>|〇|AIモデルの登録名を指定する|
|-o,--output_image_file <推論結果画像の保存先ファイル>|-|推論結果画像の保存先ファイルを指定する|
|--capture_device <device>|-|キャプチャーディバイスを指定する。`cv2.VideoCapture`の第一引数に渡される値。|
|--capture_output_type <画像の出力方法>|-|キャプチャーした画像の出力方法。現在使用していない。|
|--capture_frame_width <キャプチャーサイズ(横px)>|-|キャプチャーする画像の横px。`cv2.VideoCapture`オブジェクトの`cv2.CAP_PROP_FRAME_WIDTH`オプションに指定する値。|
|--capture_frame_height <キャプチャーサイズ(縦px)>|-|キャプチャーする画像の縦px。`cv2.VideoCapture`オブジェクトの`cv2.CAP_PROP_FRAME_HEIGHT`オプションに指定する値。|
|--capture_fps <キャプチャーFPS>|-|キャプチャーする画像のFPS。`cv2.VideoCapture`オブジェクトの`cv2.CAP_PROP_FPS`オプションに指定する値。|
|--capture_output_fps <推論結果のFPS>|-|推論結果のFPS。AIの推論速度が指定した値より高速な場合に残り時間分をsleepする|
|--output_preview|-|推論結果画像を`cv2.imshow`で表示する|
|--timeout <タイムアウト>|-|サーバーの応答が返ってくるまでの最大待ち時間|

## カスタム推論モジュールについて
AIモデルの配備`iinfer -m client -c deploy <Option>`コマンドで`--predict_type Custom`且つ`--custom_predict_py <カスタム推論pyファイル>`オプションを指定すると、カスタムモデルを配備できます。
カスタム推論pyファイルは`iinfer.app.common.Predoct`クラスを継承させたクラスを作成してください。
`iinfer.app.common.Predoct`クラスの定義は下記の通りで、継承したクラスは`create_session`と`predict`メソッドを定義してください。

``` python
from pathlib import Path
from PIL import Image
from typing import List, Tuple

class Predoct(object):
    def create_session(self, model_path:Path, model_conf_path:Path, model_provider:str, gpu_id:int=None):
        """
        推論セッションを作成する関数です。
        startコマンド実行時に呼び出されます。
        この関数内でAIモデルのロードが行われ、推論準備を完了するようにしてください。
        戻り値の推論セッションの型は問いません。

        Args:
            model_path (Path): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.

        Returns:
            推論セッション
        """
        raise NotImplementedError()

    def predict(self, session, img_width:int, img_height:int, image:Image, labels:List[str]=None, colors:List[Tuple[int]]=None):
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
|AI Task|base|Model|FrameWork|input|Memo|
|------|------|------|------|------|------|
|Object Detection|[YOLOX](https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox)|mmdetection|640x640|YOLOX-s|-|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|416x416|YOLOX-Nano|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|416x416|YOLOX-Tiny|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-s|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-m|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-l|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|onnx|640x640|YOLOX-x|*1|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-10|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-12|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|onnx|416x416|YOLOv3-12-int8|-|
|Object Detection|[TinyYOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3)|onnx|416x416|TinyYOLOv3|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11-int8|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|onnx|224x224|EfficientNet-Lite4-11-qdq|-|

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
