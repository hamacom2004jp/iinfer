from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import cmd
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PostprocessCmd(postprocess_feature.PostprocessFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'postprocess'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'cmd'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="推論結果を環境変数にセットし任意のコマンドを実行します。",
            discription_en="Set the inference result to an environment variable and execute an arbitrary command.",
            choice=[
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     discription_ja="後処理させる推論結果をファイルで指定します。",
                     discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                     discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="cmdline", type=Options.T_STR, default='cwd', required=True, multi=False, hide=False, choice=None,
                     discription_ja="実行するコマンドを指定します。設定される環境変数は `outputs` , `output_image` です。この値は一時ファイルのファイルパスです。",
                     discription_en="Specifies the command to execute. The environment variables set are `outputs` , `output_image`. The value is the file path of the temporary file."),
                dict(opt="output_image_ext", type=Options.T_STR, default="jpeg", required=True, multi=False, hide=True, choice=['bmp', 'png', 'jpeg'],
                     discription_ja="出力画像のフォーマットを指定します。指定可能な画像タイプは `bmp` , `png` , `jpeg`",
                     discription_en="Specifies the format of the output image.Acceptable image types are `bmp` , `png`, and `jpeg`."),
                dict(opt="output_maxsize", type=Options.T_INT, default=1024*1024*5, required=True, multi=False, hide=True, choice=None,
                     discription_ja="コマンド実行結果をキャプチャーする最大サイズを指定します。",
                     discription_en="Specifies the maximum size of the command execution results to be captured."),
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
        proc = None
        try:
            proc = cmd.Cmd(logger, cmdline=args.cmdline, output_image_ext=args.output_image_ext, output_maxsize=args.output_maxsize)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                    None, False, output_image_file=None, output_csv=None, pf=pf)
        if code != 0:
            return code, ret
        return 0, ret, proc
