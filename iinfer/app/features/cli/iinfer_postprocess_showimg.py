from cmdbox.app import common
from iinfer import version
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import showimg
from typing import Dict, Any, Tuple
import argparse
import logging


class PostprocessShowimg(postprocess_feature.PostprocessFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
        """
        return 'postprocess'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'showimg'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="推論結果をshowimg.htmlに転送します。",
            discription_en="Forward the inference results to showimg.html.",
            choise=[
                dict(short="i", opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None, fileio="in",
                        discription_ja="後処理させる推論結果をファイルで指定します。",
                        discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                        discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="host", type="str", default=self.default_host, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスホストを指定します。",
                        discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type="int", default=self.default_port, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスポートを指定します。",
                        discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type="str", default=self.default_pass, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                        discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type="str", default="server", required=False, multi=False, hide=True, choise=None,
                        discription_ja="推論サーバーのサービス名を指定します。省略時は `server` を使用します。",
                        discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="maxrecsize", type="int", default=1000, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーに保存する推論結果の最大レコードサイズを指定します。",
                        discription_en="Specifies the maximum record size of inference results to be stored on the Redis server."),
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
        proc = None
        try:
            proc = showimg.Showimg(logger, host=args.host, port=args.port, password=args.password, svname=args.svname, maxrecsize=args.maxrecsize)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                    None, None, output_image_file=None)
        if code != 0:
            return code, ret
        return 0, ret, proc
