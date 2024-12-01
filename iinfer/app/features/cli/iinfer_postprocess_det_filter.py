from cmdbox.app import common
from iinfer import version
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import det_filter
from typing import Dict, Any, Tuple
import argparse
import logging


class PostprocessDetFilter(postprocess_feature.PostprocessFeature):
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
        return 'det_filter'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="ObjectDetectionで検知した個所をフィルタリングします。",
            discription_en="Filter the detected area in ObjectDetection.",
            choise=[
                dict(short="i", opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None, fileio="in",
                        discription_ja="後処理させる推論結果をファイルで指定します。",
                        discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                        discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="score_th", type="float", default="0.0", required=False, multi=False, hide=False, choise=None,
                        discription_ja="bboxのクラススコアがこの値以下のものは除去します。",
                        discription_en="Remove bboxes with class scores less"),
                dict(opt="width_th", type="int", default="0", required=False, multi=False, hide=False, choise=None,
                        discription_ja="bboxの横幅がこの長さ以下のものは除去します。",
                        discription_en="Remove bboxes with a width less than this length."),
                dict(opt="height_th", type="int", default="0", required=False, multi=False, hide=False, choise=None,
                        discription_ja="bboxの縦幅がこの長さ以下のものは除去します。",
                        discription_en="Remove bboxes with a height less than this length."),
                dict(opt="classes", type="str", default="", required=False, multi=True, hide=False, choise=None,
                        discription_ja="このクラス以外のbboxは除去します。複数指定できます。",
                        discription_en="Remove bboxes other than this class. Multiple specifications are possible."),
                dict(opt="labels", type="str", default="", required=False, multi=True, hide=False, choise=None,
                        discription_ja="このラベル以外のbboxは除去します。複数指定できます。",
                        discription_en="Remove bboxes other than this label. Multiple specifications are possible."),
                dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="推論結果画像にbbox等の描き込みを行いません。",
                        discription_en="Do not draw bboxes, etc. on the inference result image."),
                dict(short="P", opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="判定結果画像を`cv2.imshow`で表示します。",
                        discription_en="Display the judgment result image with `cv2.imshow`."),
                dict(opt="output_image", type="file", default="", required=False, multi=False, hide=False, choise=None, fileio="out",
                        discription_ja="後処理結果画像の保存先ファイルを指定します。",
                        discription_en="Specify the destination file for saving the post-processing result image."),
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
        proc = None
        try:
            proc = det_filter.DetFilter(logger, score_th=args.score_th, width_th=args.width_th, height_th=args.height_th,
                                        classes=args.classes, labels=args.labels, nodraw=args.nodraw, output_preview=args.output_preview)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                    args.output_json, args.output_json_append, output_image_file=args.output_image)
        if code != 0:
            return code, ret
        return 0, ret, proc