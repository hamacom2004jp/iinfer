from cmdbox.app import common
from iinfer import version
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import httpreq
from typing import Dict, Any, Tuple
import argparse
import logging


class PostprocessHttpreq(postprocess_feature.PostprocessFeature):
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
        return 'httpreq'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="推論結果を指定したHTTPサーバーに送信します。",
            discription_en="Send the inference result to the specified HTTP server.",
            choise=[
                dict(short="i", opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None, fileio="in",
                        discription_ja="後処理させる推論結果をファイルで指定します。",
                        discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                        discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="json_without_img", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="JSONの送信時に画像を含めず送信します。",
                        discription_en="Send JSON without including images when sending JSON."),
                dict(opt="fileup_name", type="str", default="file", required=True, multi=False, hide=False, choise=None,
                        discription_ja="推論結果の画像をPOSTするときのパラメータ名を指定します。省略すると `file` が使用されます。",
                        discription_en="Specify the parameter name when posting the image of the inference result. If omitted, `file` is used."),
                dict(opt="outputs_url", type="str", default=None, required=True, multi=False, hide=False, choise=None,
                        discription_ja="推論結果のJSONをPOSTするURLを指定します。",
                        discription_en="Specify the URL to POST the JSON of the inference result."),
                dict(opt="output_image_url", type="str", default=None, required=False, multi=False, hide=False, choise=None,
                        discription_ja="推論結果の画像をPOSTするURLを指定します。",
                        discription_en="Specify the URL to POST the image of the inference result."),
                dict(opt="output_image_ext", type="str", default='jpeg', required=False, multi=False, hide=False, choise=['bmp', 'png', 'jpeg'],
                        discription_ja="推論結果の画像をフォーマットを指定します。 `bmp` , `png` , `jpeg` が指定できます。",
                        discription_en="Specifies the format of the image of the inference result.You can specify `bmp` , `png`, or `jpeg`."),
                dict(opt="output_image_prefix", type="str", default='output_', required=False, multi=False, hide=False, choise=None,
                        discription_ja="推論結果の画像の接頭語を指定します。省略すると `output_` が使用されます。",
                        discription_en="Specifies the prefix of the inferred result image. If omitted, `output_` is used."),
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
            proc = httpreq.Httpreq(logger, fileup_name=args.fileup_name, outputs_url=args.outputs_url, output_image_url=args.output_image_url,
                                   output_image_ext=args.output_image_ext, output_image_prefix=args.output_image_prefix,
                                   json_without_img=args.json_without_img)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                    None, False, output_image_file=None)
        if code != 0:
            return code, ret
        return 0, ret, proc
