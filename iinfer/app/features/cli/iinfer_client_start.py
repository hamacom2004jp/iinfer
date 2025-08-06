from cmdbox.app import common, feature
from cmdbox.app.commons import redis_client
from cmdbox.app.options import Options
from motpy import MultiObjectTracker
from iinfer.app import client, common as cmn
from iinfer.app.commons import module
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging
import json


class ClientStart(feature.OneshotNotifyEdgeFeature):
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
        return 'start'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            description_ja="AIモデルを指定して推論サーバーを起動します。",
            description_en="Start the inference server by specifying the AI model.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(short="n", opt="name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="削除するAIモデルの登録名を指定します。",
                     description_en="Specify the registration name of the AI model to be deleted.",
                     test_true={"yolox":"yolox",
                                "upernet":"upernet",
                                "san":"san",
                                "pspnet":"pspnet",
                                "swin":"swin",
                                "lnsightface":"lnsightface",
                                "yolo3":"yolo3",
                                "effnet":"effnet",
                                "custom":"custom"}),
                dict(opt="model_provider", type=Options.T_STR, default="CPUExecutionProvider", required=False, multi=False, hide=True,
                     choice=['CPUExecutionProvider', 'CUDAExecutionProvider', 'TensorrtExecutionProvider'],
                     description_ja="ONNX形式のモデルファイルの場合に指定可能。",
                     description_en="Specify when the model file is in ONNX format.",
                     test_true={"yolox":None,
                                "upernet":None,
                                "san":None,
                                "pspnet":None,
                                "swin":None,
                                "lnsightface":"CUDAExecutionProvider",
                                "yolo3":"CUDAExecutionProvider",
                                "effnet":"CUDAExecutionProvider",
                                "custom":None}),
                dict(short="T", opt="use_track", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="ObjectDetectionタスクの場合に指定可能。motpyを使ってトラッキングID付与を行う。",
                     description_en="Specify when the task is ObjectDetection. Assign a tracking ID using motpy.",
                     test_true={"yolox":True,
                                "upernet":False,
                                "yolo3":True,
                                "effnet":False}),
                dict(opt="gpuid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="GPUのディバイスIDを指定します。",
                     description_en="Specify the device ID of the GPU.",
                     test_true={"yolox":"0"}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds.",
                     test_true={"yolox":120}),
                dict(opt="output_json", short="o" , type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a" , type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
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
        return 'start'

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

        ret = cl.start(args.name, model_provider=args.model_provider, use_track=args.use_track, gpuid=args.gpuid,
                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
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
        st = self.start(msg[1], msg[2], msg[3], (True if msg[4]=='True' else False), (None if msg[5]=='None' else msg[5]),
                        data_dir, logger, redis_cli, sessions)
        return st

    def start(self, reskey:str, name:str, model_provider:str, use_track:bool, gpuid:str,
              data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        モデルを読み込み、処理が実行できるようにする

        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            use_track (bool): Multi Object Trackerを使用するかどうか, by default False
            gpuid (int): GPU ID, by default None
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        """
        if name is None or name == "":
            logger.warning(f"Name is empty.")
            redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        deploy_dir = data_dir / name
        if name in sessions:
            logger.warning(f"{name} has already started a session.")
            redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        conf_path = deploy_dir / "conf.json"
        if not conf_path.exists():
            logger.warning(f"Conf path {str(conf_path)} does not exist")
            redis_cli.rpush(reskey, {"warn": f"Conf path {str(conf_path)} does not exist"})
            return self.RESP_WARN
        with open(conf_path, "r") as cf:
            conf = json.load(cf)
            if conf['predict_type'] != 'Custom' and cmn.BASE_MODELS[conf['predict_type']]['required_model_weight']:
                model_path = Path(conf["model_file"])
            else:
                model_path = conf["model_file"]
            if "model_conf_file" in conf and conf["model_conf_file"] is not None and len(conf["model_conf_file"]) > 0:
                model_conf_path = Path(conf["model_conf_file"][0])
            else:
                model_conf_path = None
            try:
                if "before_injection_conf" in conf and conf["before_injection_conf"] is not None:
                    before_injection_conf = dict()
                    with open(conf["before_injection_conf"], "r") as f:
                        before_injection_conf = json.load(f)
                else:
                    before_injection_conf = dict()
                if "before_injection_type" in conf and conf["before_injection_type"] is not None and len(conf["before_injection_type"]) > 0:
                    types = [t for t in conf["before_injection_type"]]
                    before_injections = module.load_before_injection_type(types, before_injection_conf, logger)
                else:
                    before_injections = None
                if "before_injection_py" in conf and conf["before_injection_py"] is not None and len(conf["before_injection_py"]) > 0:
                    paths = [Path(p) for p in conf["before_injection_py"]]
                    before_injections = [] if before_injections is None else before_injections
                    before_injections = module.load_before_injections(paths, before_injection_conf, logger)
            except Exception as e:
                logger.warning(f"Failed to load before_injection: {e}", exc_info=True)
                redis_cli.rpush(reskey, {"warn": f"Failed to load before_injection: {e}"})
                return self.RESP_WARN
            try:
                if "after_injection_conf" in conf and conf["after_injection_conf"] is not None:
                    after_injection_conf = dict()
                    with open(conf["after_injection_conf"], "r") as f:
                        after_injection_conf = json.load(f)
                else:
                    after_injection_conf = dict()
                if "after_injection_type" in conf and conf["after_injection_type"] is not None and len(conf["after_injection_type"]) > 0:
                    types = [t for t in conf["after_injection_type"]]
                    after_injections = module.load_after_injection_type(types, after_injection_conf, logger)
                else:
                    after_injections = None
                if "after_injection_py" in conf and conf["after_injection_py"] is not None and len(conf["after_injection_py"]) > 0:
                    paths = [Path(p) for p in conf["after_injection_py"]]
                    after_injections = [] if after_injections is None else after_injections
                    after_injections = module.load_after_injections(paths, after_injection_conf, logger)
                if type(model_path) is Path and not model_path.exists():
                    logger.warning(f"Model path {str(model_path)} does not exist")
                    redis_cli.rpush(reskey, {"warn": f"Model path {str(model_path)} does not exist"})
                    return self.RESP_WARN
            except Exception as e:
                logger.warning(f"Failed to load after_injection: {e}", exc_info=True)
                redis_cli.rpush(reskey, {"warn": f"Failed to load after_injection: {e}"})
                return self.RESP_WARN
            try:
                conf["custom_predict_py"] = conf["custom_predict_py"] if "custom_predict_py" in conf else None
                ret, predict_obj = module.build_predict(conf["predict_type"], conf["custom_predict_py"], logger)
                if not ret:
                    redis_cli.rpush(reskey, predict_obj)
                    return self.RESP_WARN
            except Exception as e:
                logger.warning(f"Failed to load Predict: {e}", exc_info=True)
                redis_cli.rpush(reskey, {"warn": f"Failed to load Predict: {e}"})
                return self.RESP_WARN
            if "label_file" in conf and conf["label_file"] is not None:
                label_file = Path(conf["label_file"])
                if not label_file.exists():
                    logger.warning(f"label_file path {str(label_file)} does not exist")
                    redis_cli.rpush(reskey, {"warn": f"label_file path {str(label_file)} does not exist"})
                    return self.RESP_WARN
                with open(label_file, "r") as f:
                    labels = f.read().splitlines()
            else:
                labels = None
            if "color_file" in conf and conf["color_file"] is not None:
                color_file = Path(conf["color_file"])
                if not color_file.exists():
                    logger.warning(f"color_file path {str(color_file)} does not exist")
                    redis_cli.rpush(reskey, {"warn": f"color_file path {str(color_file)} does not exist"})
                    return self.RESP_WARN
                with open(color_file, "r") as f:
                    colors = [tuple([int(c) for c in line.split(',')]) for line in f.read().splitlines()]
            else:
                colors = None
            try:
                session = predict_obj.create_session(deploy_dir, model_path, model_conf_path, model_provider, gpu_id=gpuid)
                sessions[name] = dict(
                    session=session,
                    model_img_width=conf["model_img_width"],
                    model_img_height=conf["model_img_height"],
                    predict_obj=predict_obj,
                    labels=labels,
                    colors=colors,
                    tracker=MultiObjectTracker(dt=0.1) if use_track else None,
                    before_injections=before_injections,
                    after_injections=after_injections
                )
            except Exception as e:
                logger.warning(f"Failed to create session: {e}", exc_info=True)
                redis_cli.rpush(reskey, {"warn": f"Failed to create session: {e}"})
                return self.RESP_WARN
        logger.info(f"Successful start of {name} session.")
        redis_cli.rpush(reskey, {"success": f"Successful start of {name} session."})
        return self.RESP_SUCCESS
