from cmdbox.app import common, feature
from cmdbox.app.commons import redis_client
from iinfer import version
from iinfer.app import client
from pathlib import Path
from typing import Dict, Any, Tuple, List
import argparse
import logging
import json


class ClientDeployList(feature.Feature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
        """
        return 'client'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'deploy_list'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_TRUE,
            discription_ja="サーバーに配備されているAIモデル一覧を取得します。",
            discription_en="Get a list of AI models deployed on the server.",
            choise=[
                dict(opt="host", type="str", default=self.default_host, required=True, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスホストを指定します。",
                        discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type="int", default=self.default_port, required=True, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスポートを指定します。",
                        discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type="str", default=self.default_pass, required=True, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                        discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None,
                        discription_ja="推論サーバーのサービス名を指定します。省略時は `server` を使用します。",
                        discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="retry_count", type="int", default=3, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                        discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever.",
                        test_true={"yolox":1}),
                dict(opt="retry_interval", type="int", default=5, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                        discription_en="Specifies the number of seconds before reconnecting to the Redis server.",
                        test_true={"yolox":1},
                        test_false={"yolox":-1}),
                dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None,
                        discription_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                        discription_en="Specify the maximum waiting time until the server responds.",
                        test_true={"yolox":15},
                        test_false={"yolox":-1}),
                dict(opt="output_json", short="o" , type="file", default="", required=False, multi=False, hide=True, choise=None, fileio="out",
                        discription_ja="処理結果jsonの保存先ファイルを指定。",
                        discription_en="Specify the destination file for saving the processing result json.",
                        test_true={"yolox":None}),
                dict(opt="output_json_append", short="a" , type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="処理結果jsonファイルを追記保存します。",
                        discription_en="Save the processing result json file by appending.",
                        test_true={"yolox":False}),
                dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                        discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                        discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choise=None,
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                        discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )
    
    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'deploy_list'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
        
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        ret = cl.deploy_list(retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

        if 'success' not in ret:
            return 1, ret, cl

        return 0, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

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
        st = self.deploy_list(msg[1], data_dir, logger, redis_cli, sessions)
        return st

    def deploy_list(self, reskey:str,
                    data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        デプロイされたモデルのリストを取得する

        Args:
            reskey (str): レスポンスキー
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            dict: デプロイされたモデルのリスト
        """
        deploy_list = []
        common.mkdirs(data_dir)
        for dir in data_dir.iterdir():
            if not dir.is_dir():
                continue
            if dir.name.startswith("."):
                continue
            if dir.name in ["mmpretrain", "mmdetection", "mmsegmentation"]:
                continue
            conf_path = dir / "conf.json"
            if not conf_path.exists():
                if logger.level == logging.DEBUG:
                    logger.debug(f"Conf path {str(conf_path)} does not exist")
                continue
            with open(conf_path, "r") as cf:
                conf = json.load(cf)
                model_file = 'exists' if "model_file" in conf and conf["model_file"] is not None and Path(conf["model_file"]).exists() else None
                model_conf_file = None
                if "model_conf_file" in conf and conf["model_conf_file"] is not None and len(conf["model_conf_file"]) > 0 and Path(conf["model_conf_file"][0]).exists():
                    model_conf_file = 'exists'
                before_injection = None
                if "before_injection_py" in conf and conf["before_injection_py"] is not None and len(conf["before_injection_py"]) > 0:
                    if len([True for p in conf["before_injection_py"] if  Path(p).exists()]) > 0:
                        before_injection = 'exists'
                if "before_injection_type" in conf and conf["before_injection_type"] is not None and len(conf["before_injection_type"]) > 0:
                    before_injection = 'enabled'
                after_injection = None
                if "after_injection_py" in conf and conf["after_injection_py"] is not None and len(conf["after_injection_py"]) > 0:
                    if len([True for p in conf["after_injection_py"] if  Path(p).exists()]) > 0:
                        after_injection = 'exists'
                if "after_injection_type" in conf and conf["after_injection_type"] is not None and len(conf["after_injection_type"]) > 0:
                    after_injection = 'enabled'
                custom_predict_py = 'exists' if "custom_predict_py" in conf and conf["custom_predict_py"] is not None and Path(conf["custom_predict_py"]).exists() else None
                label_file = 'exists' if "label_file" in conf and conf["label_file"] is not None and Path(conf["label_file"]).exists() else None
                color_file = 'exists' if "color_file" in conf and conf["color_file"] is not None and Path(conf["color_file"]).exists() else None
                train_dataset = 'exists' if "train_dataset" in conf and conf["train_dataset"] is not None and Path(conf["train_dataset"]).exists() else None
                train_type = conf["train_type"] if "train_type" in conf else None
                custom_train_py = 'exists' if "custom_train_py" in conf and conf["custom_train_py"] is not None and Path(conf["custom_train_py"]).exists() else None
                row = dict(name=dir.name,
                           input=(conf["model_img_width"], conf["model_img_height"]), model_file=model_file, model_conf_file=model_conf_file,
                           predict_type=conf["predict_type"], custom_predict=custom_predict_py,
                           label_file=label_file, color_file=color_file,
                           session=dir.name in sessions,
                           mot=dir.name in sessions and sessions[dir.name]['tracker'] is not None,
                           before_injection_py=before_injection,
                           after_injection_py=after_injection,
                           train_dataset=train_dataset, train_type=train_type, custom_train=custom_train_py)
                deploy_list.append(row)
        redis_cli.rpush(reskey, {"success": deploy_list})
        return self.RESP_SCCESS
