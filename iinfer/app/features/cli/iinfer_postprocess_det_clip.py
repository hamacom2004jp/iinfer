from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import det_clip
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PostprocessDetClip(postprocess_feature.PostprocessFeature):
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
        return 'det_clip'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            description_ja="ObjectDetectionで検知した個所を切り出し、caprute形式のcsvで出力します。",
            description_en="Cut out the detected area in ObjectDetection and output it in caprute format csv.",
            choice=[
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="後処理させる推論結果をファイルで指定します。",
                     description_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="後処理させる推論結果を標準入力から読み込みます。",
                     description_en="Read the inference result to be post-processed from standard input."),
                dict(opt="image_type", type=Options.T_STR, default="capture", required=False, multi=False, hide=False, choice=['bmp', 'png', 'jpeg', 'capture'],
                     description_ja="出力する画像のタイプを指定します。",
                     description_en="Specify the type of image to output."),
                dict(opt="clip_margin", type=Options.T_INT, default=0, required=False, multi=False, hide=False, choice=None,
                     description_ja="検視したbboxの周囲に余白を設けるピクセル数です。但し、元画像の外側に余白が出る場合は、確保できるだけ余白を取得します。",
                     description_en="The number of pixels to provide margin around the bbox inspected. However, if there is a margin outside the original image, as much margin as possible is obtained."),
                dict(opt="output_csv", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="内容をcsvで保存します。これを指定した場合、標準出力は行いません。",
                     description_en="Save the contents in csv. If this is specified, no standard output will be performed."),
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
        proc = None
        try:
            proc = det_clip.DetClip(logger, image_type=args.image_type, clip_margin=args.clip_margin)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                    None, False, output_image_file=None, output_csv=args.output_csv, pf=pf)
        if code != 0:
            return code, ret
        return self.RESP_SUCCESS, ret, proc
