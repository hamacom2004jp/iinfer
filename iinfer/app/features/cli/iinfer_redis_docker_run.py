from cmdbox.app import common, feature
from cmdbox.app.options import Options
from iinfer.app import redis
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class RedisDockerRun(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'redis'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'docker_run'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            description_ja="installモードで `iinfer -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。",
            description_en="If you are running `iinfer -m install -c server` in install mode, use `docker-compose up -d`.",
            choice=[
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="wsl_name", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="Windowsの場合はWSLのディストリビューションの名前を指定します。",
                     description_en="For Windows, specify the name of the WSL distribution."),
                dict(opt="wsl_user", type=Options.T_STR, default="ubuntu", required=False, multi=False, hide=True, choice=None,
                     description_ja="Windowsの場合はWSL内のユーザー名を指定します。",
                     description_en="For Windows, specify the user name in WSL."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
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
        rd = redis.Redis(logger=logger, wsl_name=args.wsl_name, wsl_user=args.wsl_user)
        ret = rd.docker_run(args.port, args.password)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        return 0, ret, rd
