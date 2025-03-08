from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import csv
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PostprocessCsv(postprocess_feature.PostprocessFeature):
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
        return 'csv'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="推論結果をCSVファイルに変換します。",
            discription_en="Convert the inference result to a CSV file.",
            choice=[
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     discription_ja="後処理させる推論結果をファイルで指定します。",
                     discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                     discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="out_headers", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     discription_ja="出力するヘッダーを指定します。複数指定できます。",
                     discription_en="Specify the headers to output. Multiple specifications are possible."),
                dict(opt="noheader", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="ヘッダー行の出力を行いません。",
                     discription_en="Do not output the header row."),
                dict(opt="output_csv", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="内容をcsvで保存する。これを指定した場合、標準出力は行いません。",
                     discription_en="Save the contents in csv. If this is specified, no standard output will be performed."),
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
            proc = csv.Csv(logger, out_headers=args.out_headers, noheader=args.noheader)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                    None, False, output_image_file=None, output_csv=args.output_csv, pf=pf)
        if code != 0:
            return code, ret
        return 0, ret, proc
