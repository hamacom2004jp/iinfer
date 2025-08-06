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
            description_ja="webcapモードを起動します。",
            description_en="Start webcap mode.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None,
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="allow_host", type=Options.T_STR, default="0.0.0.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `0.0.0.0` を使用します。",
                     description_en="If omitted, `0.0.0.0` is used."),
                dict(opt="listen_webcap_port", type=Options.T_INT, default="8082", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `8082` を使用します。",
                     description_en="If omitted, `8082` is used."),
                dict(opt="image_type", type=Options.T_STR, default="capture", required=True, multi=False, hide=False, choice=['bmp', 'png', 'jpeg', 'capture'],
                     description_ja="出力する画像のタイプを指定します。",
                     description_en="Specify the type of image to output."),
                dict(opt="outputs_key", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="webcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。",
                     description_en="Specify items to be displayed on the webcap screens. If omitted, all items are displayed."),
                dict(opt="capture_frame_width", type=Options.T_INT, default=640, required=False, multi=False, hide=True, choice=None,
                     description_ja="キャプチャーする画像の横px。受信した画像をリサイズします。",
                     description_en="Width px of the image to be captured. Resize the received image."),
                dict(opt="capture_frame_height", type=Options.T_INT, default=480, required=False, multi=False, hide=True, choice=None,
                     description_ja="キャプチャーする画像の縦px。受信した画像をリサイズします。",
                     description_en="Height px of the image to be captured. Resize the received image."),
                dict(opt="capture_fps", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepします。",
                     description_en="FPS of the image to be captured. If the capture is faster than the specified value, sleep for the remaining time."),
                dict(opt="capture_count", type=Options.T_INT, default=5, required=False, multi=False, hide=False, choice=None,
                     description_ja="キャプチャーする回数。",
                     description_en="Number of captures."),
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
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg
        w = None
        try:
            w = web.Web.getInstance(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

            w.webcap(args.allow_host, args.listen_webcap_port, image_type=args.image_type, outputs_key=args.outputs_key,
                     capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                     capture_count=args.capture_count, capture_fps=args.capture_fps)
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass
        return self.RESP_SUCCESS, None, w
