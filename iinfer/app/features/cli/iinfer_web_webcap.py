from cmdbox.app import common, feature
from cmdbox.app.options import Options
from iinfer.app import web
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import cv2
import logging


class WebWebcap(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'web'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'webcap'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="webcapモードを起動します。",
            discription_en="Start webcap mode.",
            choice=[
                dict(opt="allow_host", type=Options.T_STR, default="0.0.0.0", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は `0.0.0.0` を使用します。",
                     discription_en="If omitted, `0.0.0.0` is used."),
                dict(opt="listen_webcap_port", type=Options.T_INT, default="8082", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は `8082` を使用します。",
                     discription_en="If omitted, `8082` is used."),
                dict(opt="image_type", type=Options.T_STR, default="capture", required=True, multi=False, hide=False, choice=['bmp', 'png', 'jpeg', 'capture'],
                     discription_ja="出力する画像のタイプを指定します。",
                     discription_en="Specify the type of image to output."),
                dict(opt="outputs_key", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     discription_ja="webcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。",
                     discription_en="Specify items to be displayed on the webcap screens. If omitted, all items are displayed."),
                dict(opt="capture_frame_width", type=Options.T_INT, default=640, required=False, multi=False, hide=True, choice=None,
                     discription_ja="キャプチャーする画像の横px。受信した画像をリサイズします。",
                     discription_en="Width px of the image to be captured. Resize the received image."),
                dict(opt="capture_frame_height", type=Options.T_INT, default=480, required=False, multi=False, hide=True, choice=None,
                     discription_ja="キャプチャーする画像の縦px。受信した画像をリサイズします。",
                     discription_en="Height px of the image to be captured. Resize the received image."),
                dict(opt="capture_fps", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepします。",
                     discription_en="FPS of the image to be captured. If the capture is faster than the specified value, sleep for the remaining time."),
                dict(opt="capture_count", type=Options.T_INT, default=5, required=False, multi=False, hide=False, choice=None,
                     discription_ja="キャプチャーする回数。",
                     discription_en="Number of captures."),
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
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg
        w = None
        try:
            w = web.Web(logger, Path(args.data), appcls=self.appcls, ver=self.ver)

            w.webcap(args.allow_host, args.listen_webcap_port, image_type=args.image_type, outputs_key=args.outputs_key,
                     capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                     capture_count=args.capture_count, capture_fps=args.capture_fps)
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass
        return 0, None, w
