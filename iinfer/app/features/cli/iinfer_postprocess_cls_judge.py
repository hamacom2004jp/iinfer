from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import cls_judge
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class PostprocessClsJudge(postprocess_feature.PostprocessFeature):
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
        return 'cls_judge'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            description_ja="推論結果を使用して画像分類判定を行います。",
            description_en="Perform image classification judgment using the inference result.",
            choice=[
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="後処理させる推論結果をファイルで指定します。",
                     description_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="後処理させる推論結果を標準入力から読み込みます。",
                     description_en="Read the inference result to be post-processed from standard input."),
                dict(opt="ok_score_th", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="クラススコアがこの値以上のものはok判定されます。",
                     description_en="Class scores greater than this value are judged as ok."),
                dict(opt="ok_classes", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="okクラスに含めるクラスindexを指定します。複数指定できます。",
                     description_en="Specify the class index to include in the ok class. Multiple specifications are possible."),
                dict(opt="ok_labels", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="okクラスに含めるクラスラベルを指定します。複数指定できます。",
                     description_en="Specify the class label to include in the ok class. Multiple specifications are possible."),
                dict(opt="ng_score_th", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="クラススコアがこの値以上のものはng判定されます。",
                     description_en="Class scores greater than this value are judged as ng."),
                dict(opt="ng_classes", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="ngクラスに含めるクラスindexを指定します。複数指定できます。",
                     description_en="Specify the class index to include in the ng class. Multiple specifications are possible."),
                dict(opt="ng_labels", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="ngクラスに含めるクラスラベルを指定します。複数指定できます。",
                     description_en="Specify the class label to include in the ng class. Multiple specifications are possible."),
                dict(opt="ext_score_th", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="クラススコアがこの値以上のものはgray判定されます",
                     description_en="Class scores greater than this value are judged as gray."),
                dict(opt="ext_classes", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="grayクラスに含めるクラスindexを指定します。複数指定できます。",
                     description_en="Specify the class index to include in the gray class. Multiple specifications are possible."),
                dict(opt="ext_labels", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="grayクラスに含めるクラスラベルを指定します。複数指定できます。",
                     description_en="Specify the class label to include in the gray class. Multiple specifications are possible."),
                dict(opt="nodraw", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="推論結果画像にbbox等の描き込みを行いません。",
                     description_en="Do not draw bboxes, etc. on the inference result image."),
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
            proc = cls_judge.ClaJadge(logger, ok_score_th=args.ok_score_th, ok_classes=args.ok_classes, ok_labels=args.ok_labels,
                                    ng_score_th=args.ng_score_th, ng_classes=args.ng_classes, ng_labels=args.ng_labels,
                                    ext_score_th=args.ext_score_th, ext_classes=args.ext_classes, ext_labels=args.ext_labels,
                                    nodraw=args.nodraw, output_preview=args.output_preview)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                args.output_json, args.output_json_append, output_image_file=args.output_image, pf=pf)
        if code != 0:
            return code, ret
        return self.RESP_SUCCESS, ret, proc
