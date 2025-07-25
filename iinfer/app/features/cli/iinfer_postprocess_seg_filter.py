from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import seg_filter
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PostprocessSegFilter(postprocess_feature.PostprocessFeature):
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
        return 'seg_filter'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            description_ja="SemanticSegmentationで検知した個所をフィルタリングします。",
            description_en="Filter the detected area in SemanticSegmentation.",
            choice=[
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="後処理させる推論結果をファイルで指定します。",
                     description_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="後処理させる推論結果を標準入力から読み込みます。",
                     description_en="Read the inference result to be post-processed from standard input."),
                dict(opt="del_segments", type=Options.T_BOOL, default=True, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="セグメンテーションマスクを結果から削除します。結果容量削減に効果があります。",
                     description_en="Remove the segmentation mask from the result. This reduces the result capacity."),
                dict(opt="logits_th", type=Options.T_FLOAT, default="-100.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="ピクセルごとのクラススコアがこの値以下のものは除去されます。",
                     description_en="Pixels with class scores less than this value are removed."),
                dict(opt="classes", type=Options.T_INT, default=None, required=False, multi=True, hide=True, choice=None,
                     description_ja="このクラス以外のマスクは除去します。複数指定できます。",
                     description_en="Remove areas other than this class. Multiple specifications are possible."),
                dict(opt="labels", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="このラベル以外のマスクは除去します。複数指定できます。",
                     description_en="Remove areas other than this label. Multiple specifications are possible."),
                dict(opt="nodraw", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="推論結果画像にマスクの描き込みを行いません。",
                     description_en="Do not draw masks on the inference result image."),
                dict(opt="del_logits", type=Options.T_BOOL, default=True, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="セグメンテーションスコアを結果から削除します。結果容量削減に効果があります。",
                     description_en="Remove the segmentation score from the result. This reduces the result capacity."),
                dict(short="P", opt="output_preview", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="判定結果画像を`cv2.imshow`で表示します。",
                     description_en="Display the judgment result image with `cv2.imshow`."),
                dict(opt="output_image", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="後処理結果画像の保存先ファイルを指定します。",
                     description_en="Specify the destination file for saving the post-processing result image."),
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
        proc = None
        try:
            proc = seg_filter.SegFilter(logger, logits_th=args.logits_th, classes=args.classes, labels=args.labels,
                                        nodraw=args.nodraw, del_logits=args.del_logits)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                    args.output_json, args.output_json_append, output_image_file=args.output_image, pf=pf)
        if code != 0:
            return code, ret
        return 0, ret, proc
