from cmdbox.app import common, feature
from iinfer import version
from iinfer.app import client
from typing import Dict, Any, Tuple
import cv2
import argparse
import logging
import time


class ClientCapture(feature.Feature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
        """
        return 'client'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'capture'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="クライアント側でキャプチャー画像を取得します。",
            discription_en="Get a capture image on the client side.",
            test_assert="assert result != ''",
            choise=[
                dict(opt="capture_device", type="str", default="0", required=True, multi=False, hide=False, choise=None,
                        discription_ja="キャプチャーディバイスを指定します。 `cv2.VideoCapture` の第一引数に渡される値。",
                        discription_en="Specify the capture device. The value passed to the first argument of `cv2.VideoCapture`.",
                        test_true={"jpeg":"0",},
                        test_false={"jpeg":"-1"}),
                dict(opt="image_type", type="str", default="capture", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture'],
                        discription_ja="出力する画像のタイプを指定します。",
                        discription_en="Specify the type of image to output.",
                        test_true={"jpeg":"capture",
                                "bmp":"bmp",
                                "png":"png",
                                "capture":"capture"}),
                dict(opt="capture_frame_width", type="int", default=640, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像の横px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_WIDTH` オプションに指定する値。",
                        discription_en="Width px of the image to be captured. The value to be specified in the `cv2.CAP_PROP_FRAME_WIDTH` option of the `cv2.VideoCapture` object.",
                        test_true={"jpeg":640},
                        test_false={"jpeg":-10}),
                dict(opt="capture_frame_height", type="int", default=480, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像の縦px。 `cv2.VideoCapture` オブジェクトの `cv2.CAP_PROP_FRAME_HEIGHT` オプションに指定する値。",
                        discription_en="Height px of the image to be captured. The value to be specified in the `cv2.CAP_PROP_FRAME_HEIGHT` option of the `cv2.VideoCapture` object.",
                        test_true={"jpeg":480},
                        test_false={"jpeg":-10}),
                dict(opt="capture_fps", type="int", default=5, required=False, multi=False, hide=True, choise=None,
                        discription_ja="キャプチャーする画像のFPS。キャプチャーが指定した値より高速な場合に残り時間分をsleepします。",
                        discription_en="FPS of the image to be captured. If the capture is faster than the specified value, sleep for the remaining time.",
                        test_true={"jpeg":5},
                        test_false={"jpeg":-1}),
                dict(opt="capture_count", type="int", default=5, required=False, multi=False, hide=False, choise=None,
                        discription_ja="キャプチャーする回数。",
                        discription_en="Number of captures.",
                        test_true={"jpeg":3},
                        test_false={"jpeg":-1}),
                dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False],
                        discription_ja="推論結果画像を `cv2.imshow` で表示します。",
                        discription_en="Display the inference result image with `cv2.imshow`.",
                        test_true={"jpeg":True}),
                dict(opt="output_csv", type="file", default="", required=False, multi=False, hide=True, choise=None, fileio="out",
                        discription_ja="入力した内容をcsvで保存します。これを指定した場合、標準出力は行いません。",
                        discription_en="Saves the input as a csv file. If this is specified, no standard output is performed.",
                        test_true={"jpeg":"capture.csv"}),
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
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        count = 0
        append = False
        ret = None
        try:
            for t,b64,h,w,c,fn in cl.capture(capture_device=args.capture_device, image_type=args.image_type,
                                capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                                capture_fps=args.capture_fps, output_preview=args.output_preview):
                ret = f"{t},"+b64+f",{h},{w},{c},{fn}"
                if args.output_csv is not None:
                    with open(args.output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                        print(ret, file=f)
                        append = True
                else: common.print_format(ret, False, tm, None, False)
                tm = time.perf_counter()
                count += 1
                if args.capture_count > 0 and count >= args.capture_count:
                    break
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass
        return 0, ret, cl
