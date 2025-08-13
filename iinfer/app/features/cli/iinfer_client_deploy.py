from cmdbox.app import common, feature
from cmdbox.app.commons import redis_client
from cmdbox.app.options import Options
from iinfer.app import client, common as cmn
from iinfer.app.commons import module
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import base64
import logging
import json
import shutil
import urllib

class ClientDeploy(feature.OneshotNotifyEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'client'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'deploy'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            description_ja="AIモデルをサーバーに配備します。",
            description_en="Deploy AI model to server.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server.",
                     test_true={"yolox":"localhost"},
                     test_false={"yolox":"redis"}),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server.",
                     test_true={"yolox":6379},
                     test_false={"yolox":6380}),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used.",
                     test_true={"yolox":"password"},
                     test_false={"yolox":"password2"}),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used.",
                     test_true={"yolox":"server"},
                     test_false={"yolox":"serverX"}),
                dict(short="n", opt="name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="AIモデルの登録名を指定します。",
                     description_en="Specify the registration name of the AI model.",
                     test_true={"yolox":"yolox",
                                "upernet":"upernet",
                                "san":"san",
                                "pspnet":"pspnet",
                                "swin":"swin",
                                "lnsightface":"lnsightface",
                                "yolo3":"yolo3",
                                "effnet":"effnet",
                                "custom":"custom"}),
                dict(opt="model_file", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="学習済みのモデルファイルのパス又はダウンロードURLを指定します。",
                     description_en="Specify the path or download URL of the trained model file.",
                     test_true={"yolox":"https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth",
                                "upernet":"https://download.openmmlab.com/mmsegmentation/v0.5/swin/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K/upernet_swin_small_patch4_window7_512x512_160k_ade20k_pretrain_224x224_1K_20210526_192015-ee2fff1c.pth",
                                "san":"https://download.openmmlab.com/mmsegmentation/v0.5/san/san-vit-b16_20230906-fd0a7684.pth",
                                "pspnet":"https://download.openmmlab.com/mmsegmentation/v0.5/pspnet/pspnet_r18b-d8_512x1024_80k_cityscapes/pspnet_r18b-d8_512x1024_80k_cityscapes_20201226_063116-26928a60.pth",
                                "swin":"https://download.openmmlab.com/mmclassification/v0/swin-transformer/swin_small_224_b16x64_300e_imagenet_20210615_110219-7f9d988b.pth",
                                "lnsightface":"https://drive.usercontent.google.com/download?id=1pKIusApEfoHKDjeBTXYB3yOQ0EtTonNE&export=download&authuser=0&confirm=t&uuid=00c74cef-3534-49a3-942b-582771fad908&at=APZUnTXNi6MNLsiK-EMqx_cRMJ8a%3A1723645526732",
                                "yolo3":"https://github.com/onnx/models/raw/main/validated/vision/object_detection_segmentation/yolov3/model/yolov3-10.onnx",
                                "effnet":"https://github.com/onnx/models/raw/main/validated/vision/classification/efficientnet-lite4/model/efficientnet-lite4-11-qdq.onnx",
                                "custom":"https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.pth"},
                     test_false={"yolox":"https://download.openmmlab.com/mmdetection/v2.0/yolox/yolox_s_8x8_300e_coco/yolox_s_8x8_300e_coco_20211121_095711-4592a793.XXX.pth"}),
                dict(opt="model_conf_file", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, fileio="in",
                     description_ja="モデル設定ファイルを指定します。複数指定可能ですが、最初に指定したファイルが `start` 時に使用されます。",
                     description_en="Specify the model configuration file. Multiple specifications are possible, but the file specified first is used at `start` time.",
                     test_true={"yolox":["iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py","iinfer/extensions/configs/mmdet/yolox_tta.py"],
                                "upernet":["iinfer/extensions/configs/mmseg/swin-small-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py",
                                            "iinfer/extensions/configs/mmseg/swin-tiny-patch4-window7-in1k-pre_upernet_8xb2-160k_ade20k-512x512.py"],
                                "san":["iinfer/extensions/configs/mmseg/san-vit-b16_coco-stuff164k-640x640.py"],
                                "pspnet":["iinfer/extensions/configs/mmseg/pspnet_r18-d8_4xb2-80k_cityscapes-512x1024.py",
                                            "iinfer/extensions/configs/mmseg/pspnet_r50-d8_4xb2-80k_cityscapes-512x1024.py"],
                                "swin":["iinfer/extensions/configs/mmpretrain/swin-small_16xb64_in1k.py"],
                                "lnsightface":None,
                                "yolo3":None,
                                "effnet":None,
                                "custom":["iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py","iinfer/extensions/configs/mmdet/yolox_tta.py"]},
                     test_false={"yolox":["iinfer/extensions/configs/mmdet/yolox_s_8xb8-300e_coco.py","iinfer/extensions/configs/mmdet/yolox_tta.XX"]}),
                dict(opt="model_img_width", type=Options.T_INT, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="AIモデルのINPUTサイズ(横px)を指定します。",
                     description_en="Specify the INPUT size (width px) of the AI model.",
                     test_true={"yolox":640,
                                "upernet":512,
                                "san":640,
                                "pspnet":512,
                                "swin":384,
                                "lnsightface":640,
                                "yolo3":416,
                                "effnet":224,
                                "custom":640}),
                dict(opt="model_img_height", type=Options.T_INT, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="AIモデルのINPUTサイズ(縦px)を指定します。",
                     description_en="Specify the INPUT size (height px) of the AI model.",
                     test_true={"yolox":640,
                                "upernet":512,
                                "san":640,
                                "pspnet":512,
                                "swin":384,
                                "lnsightface":640,
                                "yolo3":416,
                                "effnet":224,
                                "custom":640}),
                dict(opt="predict_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=['','Custom']+[key for key in cmn.BASE_MODELS.keys()],
                     description_ja="AIモデルの推論タイプを指定します。",
                     description_en="Specify the inference type of the AI model.",
                     choice_show=dict(Custom=["custom_predict_py"]),
                     test_true={"yolox":"mmdet_det_YoloX",
                                "upernet":"mmseg_seg_SwinUpernet",
                                "san":"mmseg_seg_San",
                                "pspnet":"mmseg_seg_PSPNet",
                                "swin":"mmpretrain_cls_swin",
                                "lnsightface":"insightface_det",
                                "yolo3":"onnx_det_YoloV3",
                                "effnet":"onnx_cls_EfficientNet_Lite4",
                                "custom":"Custom"}),
                dict(opt="custom_predict_py", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="独自の推論タイプを作成するときに指定。この時は `--predict_type Custom` を指定。",
                     description_en="Specify when creating a custom inference type. In this case, specify `--predict_type Custom`.",
                     test_true={"yolox":None,
                                "custom":"iinfer/tools/datas/predicts/mmdet_det_YoloX2.py"}),
                dict(opt="label_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="推論結果のクラスラベルファイルを指定。改行区切りでラベル名(行indexがクラスと一致する)を指定したファイル。",
                     description_en="Specify the class label file of the inference result. A file specifying the label name (the row index matches the class) separated by line breaks.",
                     test_true={"yolox":"iinfer/extensions/label_coco.txt",
                                "upernet":"iinfer/extensions/label_imagenet1k.txt",
                                "san":"iinfer/extensions/label_imagenet1k.txt",
                                "pspnet":"iinfer/extensions/label_cityscapes.txt",
                                "swin":"iinfer/extensions/label_imagenet1k.txt",
                                "lnsightface":None,
                                "yolo3":None,
                                "effnet":None,
                                "custom":"iinfer/extensions/label_coco.txt"},
                     test_false={"yolox":"iinfer/extensions/label_coco.ttt"}),
                dict(opt="color_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="推論結果の可視化画像の色ファイルを指定。改行区切りで色(行indexがクラスと一致する)を指定したファイル。",
                     description_en="Specify the color file of the visualization image of the inference result. A file specifying the color (the row index matches the class) separated by line breaks.",
                     test_true={"yolox":None}),
                dict(opt="before_injection_type", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=['']+[key for key in cmn.BASE_BREFORE_INJECTIONS.keys()],
                     description_ja="前処理を実行させるときに指定。",
                     description_en="Specify when you want to execute preprocessing.",
                     test_true={"yolox":[None, "before_grayimg_injection"]},
                     test_false={"yolox":["before_grayimg_injection2"]}),
                dict(opt="before_injection_conf", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="前処理に対する設定ファイルを指定。",
                     description_en="Specify the setting file for preprocessing.",
                     test_true={"yolox":"iinfer/tools/datas/injections/before_injection.json"},
                     test_false={"yolox":"iinfer/tools/datas/injections/before_injection.XXX"}),
                dict(opt="before_injection_py", type=Options.T_FILE, default=None, required=False, multi=True, hide=True, choice=None, fileio="in",
                     description_ja="独自の前処理を作成するときに指定。",
                     description_en="Specify when creating a custom preprocessing.",
                     test_true={"yolox":None,
                                "custom":"iinfer/tools/datas/injections/before_grayimg_injection2.py"},
                     test_false={"yolox":None,
                                 "custom":"iinfer/tools/datas/injections/before_grayimg_injection2.XXX"}),
                dict(opt="after_injection_type", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=['']+[key for key in cmn.BASE_AFTER_INJECTIONS.keys()],
                     description_ja="後処理を作成させるときに指定。",
                     description_en="Specify when you want to create post-processing.",
                     test_true={"yolox":["after_det_filter_injection","after_det_judge_injection"],
                                "upernet":["after_seg_filter_injection","after_seg_bbox_injection","after_det_filter_injection"],
                                "san":["after_seg_filter_injection","after_seg_bbox_injection","after_det_filter_injection"],
                                "pspnet":["after_seg_filter_injection","after_seg_bbox_injection","after_det_filter_injection"],
                                "swin":["after_cls_judge_injection"],
                                "lnsightface":None,
                                "yolo3":["after_det_filter_injection","after_det_judge_injection"],
                                "effnet":["after_cls_judge_injection"],
                                "custom":["after_det_filter_injection","after_det_judge_injection"]},
                     test_false={"yolox":["after_det_filter_injection","after_det_judge_injection2"]}),
                dict(opt="after_injection_conf", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="後処理に対する設定ファイルを指定。",
                     description_en="Specify the setting file for post-processing.",
                     test_true={"yolox":"iinfer/tools/datas/injections/after_injection.json"},
                     test_false={"yolox":"iinfer/tools/datas/injections/after_injection.XXX"}),
                dict(opt="after_injection_py", type=Options.T_FILE, default=None, required=False, multi=True, hide=True, choice=None, fileio="in",
                     description_ja="独自の後処理を作成するときに指定。",
                     description_en="Specify when creating custom post-processing.",
                     test_true={"yolox":None,
                                "custom":"iinfer/tools/datas/injections/after_det_filter_injection2.py"},
                     test_false={"yolox":None,
                                    "custom":"iinfer/tools/datas/injections/after_det_filter_injection2.XXX"}),
                dict(opt="overwrite", type=Options.T_BOOL, default=True, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="デプロイ済みであっても上書きする指定。",
                     description_en="Specify to overwrite even if it is already deployed.",
                     test_true={"yolox":True}),
                dict(opt="train_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=['','Custom']+[key for key in cmn.BASE_TRAIN_MODELS.keys()],
                     description_ja="AIモデルの学習タイプを指定します。",
                     description_en="Specify the train type of the AI model.",
                     choice_show=dict(**{key:["train_dataset","train_dataset_upload"] for key in list(cmn.BASE_TRAIN_MODELS.keys())},
                                         Custom=["train_dataset","train_dataset_upload","custom_train_py"]),
                     test_true={"yolox":"mmdet_det_YoloX",
                                "upernet":"mmseg_seg_SwinUpernet",
                                "san":"mmseg_seg_San",
                                "pspnet":"mmseg_seg_PSPNet",
                                "swin":"mmpretrain_cls_swin",
                                "lnsightface":None,
                                "yolo3":None,
                                "effnet":None,
                                "custom":"Custom"}),
                dict(opt="train_dataset", type=Options.T_DIR, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="データセットディレクトリを指定します。",
                     description_en="Specifies the data set directory.",
                     test_true={"yolox":"iinfer/extensions/data",
                                "lnsightface":None,
                                "yolo3":None,
                                "effnet":None}),
                dict(opt="train_dataset_upload", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="データセットをサーバーにアップロードします。",
                     description_en="Upload the data set to the server.",
                     test_true={"yolox":True,
                                "lnsightface":False,
                                "yolo3":False,
                                "effnet":False}),
                dict(opt="custom_train_py", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="独自の学習タイプを作成するときに指定。この時は `--train_type Custom` を指定。",
                     description_en="Specify when creating a custom train type. In this case, specify `--train_type Custom`.",
                     test_true={"yolox":None,
                                "custom":"iinfer/tools/datas/trains/mmdet_det_YoloX2.py"}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever.",
                     test_true={"yolox":1}),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server.",
                     test_true={"yolox":1}),
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=False, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds.",
                     test_true={"yolox":60}),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json.",
                     test_true={"yolox":None,
                                "custom":"pred.json"}),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending.",
                     test_true={"yolox":False}),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'deploy'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        if args.model_conf_file is not None:
            args.model_conf_file = [Path(f) for f in args.model_conf_file if f is not None and f != '']
        if args.before_injection_py is not None:
            args.before_injection_py = [Path(f) for f in args.before_injection_py if f is not None and f != '']
        if args.after_injection_py is not None:
            args.after_injection_py = [Path(f) for f in args.after_injection_py if f is not None and f != '']
        args.custom_predict_py = Path(args.custom_predict_py) if args.custom_predict_py is not None else None
        args.label_file = Path(args.label_file) if args.label_file is not None else None
        args.color_file = Path(args.color_file) if args.color_file is not None else None
        args.before_injection_conf = Path(args.before_injection_conf) if args.before_injection_conf is not None else None
        args.after_injection_conf = Path(args.after_injection_conf) if args.after_injection_conf is not None else None

        args.train_dataset = Path(args.train_dataset) if args.train_dataset is not None else None
        args.custom_train_py = Path(args.custom_train_py) if args.custom_train_py is not None else None

        ret = cl.deploy(args.name, args.model_img_width, args.model_img_height, args.model_file, args.model_conf_file, args.predict_type,
                        args.custom_predict_py, label_file=args.label_file, color_file=args.color_file,
                        before_injection_conf=args.before_injection_conf, before_injection_type=args.before_injection_type, before_injection_py=args.before_injection_py,
                        after_injection_conf=args.after_injection_conf, after_injection_type=args.after_injection_type, after_injection_py=args.after_injection_py,
                        train_dataset=args.train_dataset, train_dataset_upload=args.train_dataset_upload, train_type=args.train_type, custom_train_py=args.custom_train_py,
                        overwrite=args.overwrite, retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return True

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """

        if msg[7] == 'None':
            model_bin = None
        else:
            model_bin = base64.b64decode(msg[7])
        if msg[8] == 'None':
            model_conf_file = None
        else:
            model_conf_file = msg[8].split(',')
        if msg[9] == 'None':
            model_conf_bin = None
        else:
            model_conf_bin = [base64.b64decode(m) for m in msg[9].split(',')]
        if msg[10] == 'None':
            custom_predict_py = None
        else:
            custom_predict_py = base64.b64decode(msg[10])
        if msg[11] == 'None':
            label_txt = None
        else:
            label_txt = base64.b64decode(msg[11])
        if msg[12] == 'None':
            color_txt = None
        else:
            color_txt = base64.b64decode(msg[12])
        if msg[13] == 'None':
            before_injection_conf = None
        else:
            before_injection_conf = base64.b64decode(msg[13])
        if msg[14] == 'None':
            before_injection_type = None
        else:
            before_injection_type = msg[14].split(',')
        if msg[15] == 'None':
            before_injection_py = None
        else:
            before_injection_py = msg[15].split(',')
        if msg[16] == 'None':
            before_injection_bin = None
        else:
            before_injection_bin = [base64.b64decode(m) for m in msg[16].split(',')]
        if msg[17] == 'None':
            after_injection_conf = None
        else:
            after_injection_conf = base64.b64decode(msg[17])
        if msg[18] == 'None':
            after_injection_type = None
        else:
            after_injection_type = msg[18].split(',')
        if msg[19] == 'None':
            after_injection_py = None
        else:
            after_injection_py = msg[19].split(',')
        if msg[20] == 'None':
            after_injection_bin = None
        else:
            after_injection_bin = [base64.b64decode(m) for m in msg[20].split(',')]
        if msg[21] == 'None':
            train_dataset = None
        else:
            train_dataset = msg[21]
        if msg[22] == 'None':
            train_type = None
        else:
            train_type = msg[22]
        if msg[23] == 'None':
            custom_train_py = None
        else:
            custom_train_py = base64.b64decode(msg[23])
        if msg[24] == 'True':
            overwrite = True
        else:
            overwrite = False

        st = self.deploy(msg[1], msg[2], int(msg[3]), int(msg[4]), msg[5], msg[6],
                            model_bin, model_conf_file, model_conf_bin, custom_predict_py, label_txt, color_txt,
                            before_injection_conf, before_injection_type, before_injection_py, before_injection_bin,
                            after_injection_conf, after_injection_type, after_injection_py, after_injection_bin,
                            train_dataset, train_type, custom_train_py, overwrite,
                            data_dir, logger, redis_cli, sessions)

        return st

    def deploy(self, reskey:str, name:str, model_img_width:int, model_img_height:int, predict_type:str,
               model_file:str, model_bin:bytes, model_conf_file:List[str], model_conf_bin:List[bytes],
               custom_predict_py:bytes, label_txt:bytes, color_txt:bytes,
               before_injection_conf:bytes, before_injection_type:List[str], before_injection_py:List[str], before_injection_bin:List[bytes],
               after_injection_conf:bytes, after_injection_type:List[str], after_injection_py:List[str], after_injection_bin:List[bytes],
               train_dataset:str, train_type:str, custom_train_py:bytes, overwrite:bool,
               data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]):
        """
        モデルをデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            predict_type (str): 推論方法のタイプ
            model_file (str): モデルのファイル名
            model_bin (bytes): モデルファイル
            model_conf_file (List[str]): モデル設定のファイル名
            model_conf_bin (List[bytes]): モデル設定ファイル
            custom_predict_py (bytes): 推論のPythonスクリプト
            label_txt (bytes): ラベルファイル
            color_txt (bytes): 色設定ファイル
            before_injection_conf (bytes): 推論前処理の設定ファイル
            before_injection_type (List[str]): 推論前処理のタイプ
            before_injection_py (List[str]): 推論前処理のPythonスクリプトファイル名
            before_injection_bin (List[bytes]): 推論前処理のPythonスクリプト
            after_injection_conf (bytes): 推論後処理の設定ファイル
            after_injection_type (List[str]): 推論後処理のタイプ
            after_injection_py (List[str]): 推論後処理のPythonスクリプトファイル名
            after_injection_bin (List[bytes]): 推論後処理のPythonスクリプト
            train_dataset (str): 学習データセットのパス
            train_type (str): 学習方法のタイプ
            custom_train_py (bytes): 学習のPythonスクリプト
            overwrite (bool): 上書きするかどうか
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        """
        if name is None or name == "":
            logger.warning(f"Name is empty.")
            redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if model_file is None or model_file == "":
            logger.warning(f"model_file is empty.")
            redis_cli.rpush(reskey, {"warn": f"model_file is empty."})
            return self.RESP_WARN
        if model_img_width is None or model_img_width <= 0:
            logger.warning(f"Image width is invalid.")
            redis_cli.rpush(reskey, {"warn": f"Image width is invalid."})
            return self.RESP_WARN
        if model_img_height is None or model_img_height <= 0:
            logger.warning(f"Image height is invalid.")
            redis_cli.rpush(reskey, {"warn": f"Image height is invalid."})
            return self.RESP_WARN

        deploy_dir = data_dir / name
        if name in sessions:
            logger.warning(f"{name} has already started a session.")
            redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        if not overwrite and deploy_dir.exists():
            logger.warning(f"Could not be deployed. '{deploy_dir}' already exists")
            redis_cli.rpush(reskey, {"warn": f"Could not be deployed. '{deploy_dir}' already exists"})
            return self.RESP_WARN

        if predict_type != "Custom":
            if predict_type not in cmn.BASE_MODELS:
                logger.warning(f"Incorrect predict_type. '{predict_type}'")
                redis_cli.rpush(reskey, {"warn": f"Incorrect predict_type. '{predict_type}'"})
                return self.RESP_WARN
            if cmn.BASE_MODELS[predict_type]['required_model_conf']==True and model_conf_file is None:
                logger.warning(f"model_conf_file is None.")
                redis_cli.rpush(reskey, {"warn": f"model_conf_file is None."})
                return self.RESP_WARN

        common.mkdirs(deploy_dir)
        def _save_s(logger:logging.Logger, file:str, data:bytes, ret_fn:bool=False):
            if file is None or data is None:
                return False, None
            file = deploy_dir / file
            with open(file, "wb") as f:
                f.write(data)
                logger.info(f"Save {file} to {str(deploy_dir)}")
            return True, file if ret_fn else None

        if model_file.startswith("http") and (model_bin is None or model_bin == ''):
            model_path = deploy_dir / urllib.parse.urlparse(model_file).path.split('/')[-1]
            if not model_path.exists():
                logger.info(f"Downloading. {model_file}")
                urllib.request.urlretrieve(model_file, model_path)
                logger.info(f"Save {model_path}")
            else:
                logger.info(f"Already exists. {model_path}")
            model_file = model_path
        else:
            ret, model_file = _save_s(logger, model_file, model_bin, ret_fn=True)

        ret, before_injection_conf = _save_s(logger, "before_injection_conf.json", before_injection_conf, ret_fn=True)
        ret, after_injection_conf = _save_s(logger, "after_injection_conf.json", after_injection_conf, ret_fn=True)

        def _save_m(logger:logging.Logger, name:str, files:List[str], datas:List[bytes]):
            if files is not None and datas is None:
                logger.warning(f"{name}_file is not None but {name}_bin is None.")
                redis_cli.rpush(reskey, {"warn": f"{name}_file is not None but {name}_bin is None."})
                return False, files
            if files is None and datas is not None:
                logger.warning(f"{name}_file is None but {name}_bin is not None.")
                redis_cli.rpush(reskey, {"warn": f"{name}_file is None but {name}_bin is not None."})
                return False, files
            if files is not None:
                files = [deploy_dir / cf for cf in files if cf is not None and cf != '']
                for i, cf in enumerate(files):
                    with open(cf, "wb") as f:
                        f.write(datas[i])
                        logger.info(f"Save {cf} to {str(deploy_dir)}")
            return True, files
        ret, model_conf_file = _save_m(logger, 'model_conf', model_conf_file, model_conf_bin)
        if not ret: return self.RESP_WARN
        ret, before_injection_py = _save_m(logger, 'before_injection', before_injection_py, before_injection_bin)
        if not ret: return self.RESP_WARN
        ret, after_injection_py = _save_m(logger, 'after_injection', after_injection_py, after_injection_bin)
        if not ret: return self.RESP_WARN
        ret, custom_predict_file = _save_s(logger, 'custom_predict.py', custom_predict_py, ret_fn=True)
        ret, label_file = _save_s(logger, 'label.txt', label_txt, ret_fn=True)
        ret, color_file = _save_s(logger, 'color.txt', color_txt, ret_fn=True)

        if train_dataset is not None:
            train_dataset = deploy_dir / train_dataset
        else:
            train_dataset = None
        ret, custom_train_file = _save_s(logger, "custom_train.py", custom_train_py, ret_fn=True)

        with open(deploy_dir / "conf.json", "w") as f:
            conf = dict(appid=self.ver.__appid__, model_img_width=model_img_width, model_img_height=model_img_height, predict_type=predict_type,
                        model_file=model_file, model_conf_file=model_conf_file, custom_predict_py=(custom_predict_file if custom_predict_file is not None else None),
                        label_file=label_file, color_file=color_file, before_injection_conf=before_injection_conf, after_injection_conf=after_injection_conf,
                        before_injection_type=before_injection_type, after_injection_type=after_injection_type,
                        before_injection_py=before_injection_py, after_injection_py=after_injection_py,
                        train_dataset=train_dataset, train_type=train_type, custom_train_py=(custom_train_file if custom_train_file is not None else None),
                        deploy_dir=deploy_dir)
            json.dump(conf, f, default=common.default_json_enc, indent=4)
            logger.info(f"Save conf.json to {str(deploy_dir)}")

        self._gitpull(data_dir, logger, redis_cli, reskey, deploy_dir, predict_type)

        try:
            ret, predict_obj = module.build_predict(conf["predict_type"], conf["custom_predict_py"], logger)
            if not ret:
                redis_cli.rpush(reskey, predict_obj)
                return self.RESP_WARN
            predict_obj.post_deploy(deploy_dir, conf)
        except Exception as e:
            logger.warning(f"Failed to load Predict: {e}", exc_info=True)
            redis_cli.rpush(reskey, {"warn": f"Failed to load Predict: {e}"})
            return self.RESP_WARN

        redis_cli.rpush(reskey, {"success": f"Save conf.json to {str(deploy_dir)}"})
        return self.RESP_SUCCESS

    def _gitpull(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, reskey:str, deploy_dir:Path, predict_type:str):
        if predict_type.startswith('mmpretrain_'):
            if not (data_dir / "mmpretrain").exists():
                returncode, _, _cmd = common.cmd(f'cd {data_dir} && git clone https://github.com/open-mmlab/mmpretrain.git', logger=logger)
                if returncode != 0:
                    logger.warning(f"Failed to git clone mmpretrain. cmd: {_cmd}")
                    redis_cli.rpush(reskey, {"error": f"Failed to git clone mmpretrain. cmd: {_cmd}"})
                    return self.RESP_ERROR
            shutil.copytree(data_dir / "mmpretrain" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            logger.info(f"Copy mmpretrain configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmdet_'):
            if not (data_dir / "mmdetection").exists():
                returncode, _, _cmd = common.cmd(f'cd {data_dir} && git clone https://github.com/open-mmlab/mmdetection.git', logger=logger)
                if returncode != 0:
                    logger.warning(f"Failed to git clone mmdetection. cmd: {_cmd}")
                    redis_cli.rpush(reskey, {"error": f"Failed to git clone mmdetection. cmd: {_cmd}"})
                    return self.RESP_ERROR
            shutil.copytree(data_dir / "mmdetection" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            logger.info(f"Copy mmdetection configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmseg_'):
            if not (data_dir / "mmsegmentation").exists():
                returncode, _, _cmd = common.cmd(f'cd {data_dir} && git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=logger)
                if returncode != 0:
                    logger.warning(f"Failed to git clone mmsegmentation. cmd: {_cmd}")
                    redis_cli.rpush(reskey, {"error": f"Failed to git clone mmsegmentation. cmd: {_cmd}"})
                    return self.RESP_ERROR
            shutil.copytree(data_dir / "mmsegmentation" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            logger.info(f"Copy mmsegmentation configs to {str(deploy_dir / 'configs')}")
