# iinfer (Image Inference Application)

onnx又はmmlabフォーマットのAIモデルファイルを実行するアプリケーションです。
ドキュメントは[こちら](https://hamacom2004jp.github.io/iinfer/)。

## iinferの動作イメージ

![iinferの動作イメージ](https://github.com/hamacom2004jp/iinfer/raw/main/docs_src/static/orverview.drawio.png)

1. **iinfer client** は **imageファイル** や **camera** から画像を取得し、 **推論結果 predict.json** を出力します。
2. **iinfer server** は推論を行うサーバーです。 **iinfer client** からの要求に応えて、推論結果を **iinfer client** に返します。
3. **iinfer server** は予め **ai model** をロードしておくことで、推論を高速化します。
4. **iinfer client** と **iinfer server** は **Redis** 経由で通信します。
5. **iinfer server** と **Redis** は **dockerコンテナ** を使用して起動させることが出来ます。

## インストール方法

次の手順でインストールしてください:

1. pipを使用してインストールします:

```bash
pip install --upgrade pip
pip install iinfer
eval "$(register-python-argcomplete iinfer)" # Ubuntuの場合コマンドラインオプションを補完できるようにします。
```

2. コンテナをインストールして起動します。:
   ※docker及びdocker-composeを別途インストールしておく必要があります。

```bash
cd ~/
iinfer -m install -c server
docker-compose -f up -d
```

※インストールを実行したフォルダに `docker-compose.yml` が作成されます。

## iinferの使用方法

iinferを使用するには、次のコマンドを実行します:

1. guiモードで利用する場合:

![guiモードのイメージ](https://github.com/hamacom2004jp/iinfer/raw/main/docs_src/static/ss/00242_cmd_predict.jpg)

```bash
iinfer -m gui -c start
```

2. コマンドモードで利用する場合

    1. AIモデルのデプロイ:

    ```bash
    # 画像AIモデルのデプロイ
    # 推論タイプはモデルのAIタスクやアルゴリズムに合わせて指定する。指定可能なキーワードは"iinfer -m client -c predict_type_list"コマンド参照。
    iinfer -m client -c deploy -n <任意のモデル名> -f \
                               --model_file <モデルファイル> \
                               --model_conf_file <モデル設定ファイル> \
                               --predict_type <推論タイプ> \
                               --label_file <ラベルファイル>

    # デプロイされている画像AIモデルの一覧
    iinfer -m client -c deploy_list -f
    ```

    2. AIモデルのセッションを開始:

    ```bash

    # 画像AIモデルを起動させて推論可能な状態に(セッションを確保)する
    # use_trackを指定するとObjectDetectionタスクの結果に対して、MOT（Multi Object Tracking）を実行しトラッキングIDを出力する。
    iinfer -m client -c start -n <モデル名> -f \
                              --use_track
    ```

   3. 推論を実行:

    ```bash
    # 推論を実行する
    # output_previewを指定するとimshowで推論結果画像を表示する（GUI必要）
    iinfer -m client -c predict -n <モデル名> -f \
                                -i <推論させる画像ファイル> \
                                -o <推論結果の画像ファイル> \
                                --output_preview

    # カメラキャプチャー画像を元に推論を実行し、クラススコアが0.8以上の物体のみを検出する
    # --stdin --image_type capture で標準入力のキャプチャー画像を推論する
    iinfer -m client -c capture | \
    iinfer -m client -c predict -n <モデル名> \
                                --stdin \
                                --image_type capture \
                                --nodraw | \
    iinfer -m postprocess -c det_filter -f -P \
                                --stdin \
                                --score_th 0.8
    ```

    4. AIモデルのセッションを開放:

    ```bash
    # 画像AIモデルを停止させてセッションを開放
    iinfer -m client -c stop -n <モデル名> -f
    ```

## Lisence

This project is licensed under the MIT License, see the LICENSE file for details
