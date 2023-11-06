# Visual Prediction for onnx

onnxフォーマットの重みファイルを実行するWebアプリケーションです。
サポートしているAIタスクは以下のとおりです。
- Image Classification
- Object Detection


## 動作確認OS
- `Windows 10 Pro`
- `Windows 11 Pro`


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

## vp4onnxの実行方法
```
.venv\Scripts\activate
python -m vp4onnx
deactivate
```

### データの保存場所
```
pathlib.Path(HOME_DIR) / '.vp4onnx'
```

## 動作確認したモデル
|AI Task|base|Model|
|------|------|------|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-10|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-12|
|Object Detection|[YOLOv3](https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3)|YOLOv3-12-int8|

# Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
