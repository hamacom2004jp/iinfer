from cmdbox.app import common
from iinfer import version
from iinfer.app.features.cli import postprocess_feature
from iinfer.app.postprocesses import det_face_store
from typing import Dict, Any, Tuple
import argparse
import logging


class PostprocessDetFaceStore(postprocess_feature.PostprocessFeature):
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
        return 'det_face_store'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="Face Detection and Recognitionで検知した顔特徴データを個所を切り出し、顔認識ストアファイルを生成します。",
            discription_en="Cut out the face feature data detected by Face Detection and Recognition and generate a face recognition store file.",
            choise=[
                dict(short="i", opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None, fileio="in",
                        discription_ja="後処理させる推論結果をファイルで指定します。",
                        discription_en="Specify the inference result to be post-processed by file."),
                dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="後処理させる推論結果を標準入力から読み込みます。",
                        discription_en="Read the inference result to be post-processed from standard input."),
                dict(opt="image_type", type="str", default="capture", required=False, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture'],
                        discription_ja="出力する画像のタイプを指定します。",
                        discription_en="Specify the type of image to output."),
                dict(opt="face_threshold", type="float", default=0.0, required=False, multi=False, hide=False, choise=None,
                        discription_ja="顔スコアが閾値以下の場合は、顔特徴量ストアに含まれないようにします。",
                        discription_en="If the face score is below the threshold, it will not be included in the face feature store."),
                dict(opt="clip_margin", type="int", default=0, required=False, multi=False, hide=False, choise=None,
                        discription_ja="検視したbboxの周囲に余白を設けるピクセル数です。但し、元画像の外側に余白が出る場合は、確保できるだけ余白を取得します。",
                        discription_en="The number of pixels to provide margin around the bbox inspected. However, if there is a margin outside the original image, as much margin as possible is obtained."),
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
            proc = det_face_store.DetFaceStore(logger, face_threshold=args.face_threshold, image_type=args.image_type,
                                               clip_margin=args.clip_margin)
        except Exception as e:
            msg = {"warn":f"Failed to initialize. {e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, proc
        code, ret = self._exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                args.output_json, args.output_json_append, output_image_file=None)
        if code != 0:
            return code, ret
        return 0, ret, proc
