from cmdbox.app import common, feature
from iinfer import version
from iinfer.app import web
from pathlib import Path
from typing import Dict, Any, Tuple
import argparse
import cv2
import logging


class WebWebcap(feature.Feature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
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
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="webcapモードを起動します。",
            discription_en="Start webcap mode.",
            choise=[
                dict(opt="allow_host", type="str", default="0.0.0.0", required=False, multi=False, hide=False, choise=None,
                        discription_ja="省略した時は `0.0.0.0` を使用します。",
                        discription_en="If omitted, `0.0.0.0` is used."),
                dict(opt="listen_webcap_port", type="int", default="8082", required=False, multi=False, hide=False, choise=None,
                        discription_ja="省略した時は `8082` を使用します。",
                        discription_en="If omitted, `8082` is used."),
                dict(opt="signin_file", type="file", default=None, required=False, multi=False, hide=True, choise=None,
                        discription_ja="ログイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。"
                                        +"ログインファイルは、各行が1ユーザーを示し、ユーザーID、パスワード、ハッシュアルゴリズム名の順で、「 : 」で区切って記載します。"
                                        +"ハッシュアルゴリズム名は「plain」「md5」「sha1」「sha256」が指定できます。",
                        discription_en="Specify a file containing users and passwords with which they can log in. If omitted, no authentication is required."
                                        +"In the signin file, each line represents one user, in the order of user ID, password, and hash algorithm name, separated by ' :'."
                                        +"The hash algorithm name can be “plain”, “md5”, “sha1”, or “sha256”."),
                dict(opt="image_type", type="str", default="capture", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture'],
                        discription_ja="出力する画像のタイプを指定します。",
                        discription_en="Specify the type of image to output."),
                dict(opt="outputs_key", type="str", default=None, required=False, multi=True, hide=False, choise=None,
                        discription_ja="webcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。",
                        discription_en="Specify items to be displayed on the webcap screens. If omitted, all items are displayed."),
                dict(opt="capture_frame_width", type="int", default=640, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像の横px。受信した画像をリサイズします。",
                        discription_en="Width px of the image to be captured. Resize the received image."),
                dict(opt="capture_frame_height", type="int", default=480, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像の縦px。受信した画像をリサイズします。",
                        discription_en="Height px of the image to be captured. Resize the received image."),
                dict(opt="capture_fps", type="int", default=5, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepします。",
                        discription_en="FPS of the image to be captured. If the capture is faster than the specified value, sleep for the remaining time."),
                dict(opt="capture_count", type="int", default=5, required=False, multi=False, hide=False, choise=None,
                        discription_ja="キャプチャーする回数。",
                        discription_en="Number of captures."),
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
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg
        w = None
        try:
            w = web.Web(logger, Path(args.data), signin_file=args.signin_file)
            w.webcap(args.allow_host, args.listen_webcap_port, image_type=args.image_type, outputs_key=args.outputs_key,
                     capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                     capture_count=args.capture_count, capture_fps=args.capture_fps)
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass
        return 0, None, w
