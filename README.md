# Visual Prediction for onnx

onnxフォーマットの重みファイルを実行するWebアプリケーションです。
サポートしているAIタスクは以下のとおりです。
- Image Classification
- Object Detection


## 動作確認OS
- `Windows 10 Pro`
- `Windows 11 Pro`


## 実行方法

### 実行環境構築
```
git clone https://github.com/hamacom2004jp/vp4onnx.git
cd vp4onnx
python -m venv .venv
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
```

### vp4onnxの実行方法
```
.venv\Scripts\activate
python -m vp4onnx
deactivate
```

### データの保存場所
```
pathlib.Path(HOME_DIR) / '.vp4onnx'
```

# Lisence

This project is licensed under the MIT License, see the LICENSE.txt file for details
