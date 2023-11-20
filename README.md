# Visual Prediction for onnx

onnxフォーマットの重みファイルを実行するCLIアプリケーションです。
DockerコンテナのRedisサーバーを使用します。
Windowsの場合はWSL2上のLinuxの中にDockerがインストールされている必要があります。
Linuxの場合はホスト内にDockerがインストールされている必要があります。

サポートしているAIタスクは以下のとおりです。
- Image Classification
- Object Detection


## 動作確認OS
- `Windows 10 Pro`
- `Windows 11 Pro`


## インストール方法

``` cmd or bash
pip install vp4onnx
```

## vp4onnxの実行方法
``` cmd or bash
# Redisサーバーコンテナの起動（Windowsの場合）
vp4onnx -p <任意のPW> -m redis -c docker_run --wsl_name <WSLのディストリビューションの名前> --wsl_user <WSLのLinux内のDockerが使えるユーザー>

# Redisサーバーコンテナの起動（Linuxの場合）
vp4onnx -p <任意のPW> -m redis -c docker_run

# 推論処理を実行するサーバープロセスの起動
vp4onnx -p <PW> -m server -f

# 画像AIモデルのデプロイ
vp4onnx -p <PW> -m client -c deploy -n <任意のモデル名> --model_img_width <モデルの画像INPUTサイズ(横幅)> --model_img_width <モデルの画像INPUTサイズ(縦幅)> --model_onnx <モデルファイル> --predict_type <推論タイプ(後述)> --custom_predict_py <カスタム推論ファイル(後述)> -f
# predict_typeはモデルのAIタスクやアルゴリズムに合わせて指定する。指定可能なキーワードはヘルプ参照。

# デプロイされている画像AIモデルの一覧
vp4onnx -p <PW> -m client -c deploy_list -f

# 画像AIモデルを起動させて推論可能な状態に(セッションを確保)する
vp4onnx -p <PW> -m client -c start -n <モデル名> --model_provider <推論プロバイダー名(後述)> --use_mot -f
# model_providerは推論で使用する実行環境を指定する。指定可能なキーワードはヘルプ参照。
# use_motを指定するとObjectDetectionタスクの結果に対して、MOT（Multi Object Tracking）を実行しトラッキングIDを出力する。

# 推論を実行する
vp4onnx -p <PW> -m client -c predict -n <モデル名> -i <推論させる画像ファイル> -o <推論結果の画像ファイル> --output_preview -f
# output_previewを指定するとimshowで推論結果画像を表示する（GUI必要）

# 画像AIモデルを停止させてセッションを開放
vp4onnx -p <PW> -m client -c start -n <モデル名> -f

# 画像AIモデルのアンデプロイ
vp4onnx -p <PW> -m client -c undeploy -n <モデル名> -f
```

## ビデオキャプチャーによる推論
```
# カメラをキャプチャーしながら推論
vp4onnx -p <PW> -m client -c capture -n <モデル名> --output_preview -f 
# output_previewを指定するとimshowで推論結果画像を表示する（GUI必要）
# start時にuse_motオプションを使用するとトラッキングIDを出力する。
```

## その他便利なオプション
コマンドラインオプションが多いので、それを保存して再利用できるようにする（例：画像AIモデルの一覧）
``` cmd or bash
# 通常のコマンドに「-u」と「-s」オプションを追加する
vp4onnx -p <PW> -m client -c deploy_list -f -u <オプションを保存するファイル> -s

# 次から使用するときは「-u」を使用する
vp4onnx -u <オプションを保存するファイル>
```

コマンドの実行結果を見やすくする。（例：画像AIモデルの一覧）
``` cmd or bash
# 通常のコマンドに「-f」オプションを追加する
vp4onnx -p <任意PW> -m client -c deploy_list -f

# 「-f」オプションを外せば、結果はjson形式で取得できる
vp4onnx -p <任意PW> -m client -c deploy_list
```

コマンドラインオプションのヘルプ。
``` cmd or bash
vp4onnx -h
```

## vp4onnxコマンドについて
```python -m vp4onnx```の省略形です。
実体は```scripts```ディレクトリ内にあります。

### データの保存場所
```
pathlib.Path(HOME_DIR) / '.vp4onnx'
```

## 動作確認したモデル
|AI Task|base|Model|Memo|
|------|------|------|------|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-Nano|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-Tiny|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-s|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-m|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-l|*1|
|Object Detection|[YOLOX](https://github.com/Megvii-BaseDetection/YOLOX/#benchmark)|YOLOX-x|*1|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-10|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-12|-|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-12-int8|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|EfficientNet-Lite4-11|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|EfficientNet-Lite4-11-int8|-|
|Image Classification|[EfficientNet-Lite4](https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4)|EfficientNet-Lite4-11-qdq|-|

*1）[pth2onnx](https://github.com/hamacom2004jp/pth2onnx)を使用してONNX形式に変換して使用

## 開発環境構築
```
git clone https://github.com/hamacom2004jp/vp4onnx.git
cd vp4onnx
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
pip install -i https://test.pypi.org/simple/ vp4onnx
```

- 本番環境にアップロード
``` cmd or bash
twine upload --repository pypi dist/*
```

## Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
