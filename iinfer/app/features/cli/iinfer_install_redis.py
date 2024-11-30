from cmdbox.app import common, feature
from iinfer import version
from iinfer.app import install
from typing import Dict, Any, Tuple
import argparse
import logging


class InstallRedis(feature.Feature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
        """
        return 'install'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'redis'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="`redis-server` のdockerイメージをPULLします。",
            discription_en="PULL the docker image of `redis-server`.",
            choise=[
            dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None,
                discription_ja="Windowsの場合はWSLのディストリビューションの名前を指定します。",
                discription_en="For Windows, specify the name of the WSL distribution.",
                test_true={"win":"Ubuntu_docker-22.04"}),
            dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None,
                discription_ja="Windowsの場合はWSL内のユーザー名を指定します。",
                discription_en="For Windows, specify the user name in WSL.",
                test_true={"win":"ubuntu"}),
            dict(opt="output_json", short="o", type="file", default="", required=False, multi=False, hide=True, choise=None, fileio="out",
                discription_ja="処理結果jsonの保存先ファイルを指定。",
                discription_en="Specify the destination file for saving the processing result json."),
            dict(opt="output_json_append", short="a", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                discription_ja="処理結果jsonファイルを追記保存します。",
                discription_en="Save the processing result json file by appending."),
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
        inst = install.Install(logger=logger, wsl_name=args.wsl_name, wsl_user=args.wsl_user)

        ret = self.inst.redis()
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

        if 'success' not in ret:
            return 1, ret, inst
        return 0, ret, inst
