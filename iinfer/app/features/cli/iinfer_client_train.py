from cmdbox.app import common, feature
from cmdbox.app.commons import redis_client
from cmdbox.app.options import Options
from iinfer.app import client
from iinfer.app.commons import module
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging
import json
import os
import threading


class ClientTrain(feature.OneshotNotifyEdgeFeature):
    def __init__(self, appcls, ver):
        super().__init__(appcls, ver)
        self.train_thread = None

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
        return 'train'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            discription_ja="AIモデルの学習を行います。",
            discription_en="AI model training.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default="server", required=True, multi=False, hide=True, choice=None, web="readonly",
                     discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(short="n", opt="name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="AIモデルの登録名を指定します。",
                     discription_en="Specify the registration name of the AI model.",
                     test_true={"yolox":"yolox"}),
                dict(opt="overwrite", type=Options.T_BOOL, default=True, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="学習済みであっても上書きする指定。",
                     discription_en="Specify to overwrite even if it is already trained.",
                     test_true={"yolox":True}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                     discription_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=3*3600, required=False, multi=False, hide=False, choice=None,
                     discription_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     discription_en="Specify the maximum waiting time until the server responds."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="処理結果jsonの保存先ファイルを指定。",
                     discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="処理結果jsonファイルを追記保存します。",
                     discription_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
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
        return 'train'

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
            return 1, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        ret = cl.train(args.name, overwrite=args.overwrite,
                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

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
        if msg[3] == 'True':
            overwrite = True
        else:
            overwrite = False
        st = self.train(msg[1], msg[2], overwrite, data_dir, logger, redis_cli, sessions)
        return st

    def train(self, reskey:str, name:str, overwrite:bool,
              data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        モデルを学習する

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
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
            if "model_conf_file" not in conf:
                logger.warning(f"model_conf_file is not in conf.json")
                redis_cli.rpush(reskey, {"warn": f"model_conf_file is not in conf.json"})
                return self.RESP_WARN
            if "train_type" not in conf:
                logger.warning(f"train_type is not in conf.json")
                redis_cli.rpush(reskey, {"warn": f"train_type is not in conf.json"})
                return self.RESP_WARN
            custom_train_py = conf["custom_train_py"] if "custom_train_py" in conf else None
            ret, train_obj = module.build_train(conf["train_type"], custom_train_py, logger)

            def _train(train_obj, deploy_dir, model_conf_file, conf, logger):
                cwd = os.getcwd()
                try:
                    c = model_conf_file[0] if type(model_conf_file) is list and len(model_conf_file)>0 else str(model_conf_file)
                    os.chdir(deploy_dir)
                    train_obj.train(deploy_dir, c, train_cfg_options=None)
                    train_obj.post_train(deploy_dir, conf)
                except Exception as e:
                    logger.warn(f"Failed Train: {e}", exc_info=True)
                finally:
                    os.chdir(cwd)

            if self.train_thread is not None and self.train_thread.is_alive():
                logger.warning(f"Training is already running.")
                redis_cli.rpush(reskey, {"warn": f"Training is already running."})
                return self.RESP_WARN
            self.train_thread = threading.Thread(target=_train, args=(train_obj, deploy_dir, conf["model_conf_file"], conf, logger))
            self.train_thread.start()

        redis_cli.rpush(reskey, {"success": f"Training started. see {str(deploy_dir)}."})
        return self.RESP_SCCESS
