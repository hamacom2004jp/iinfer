from cmdbox.app import common, feature
from iinfer import version
from iinfer.app import client
from pathlib import Path
from typing import Dict, Any, Tuple
import argparse
import logging


class ClientReadDir(feature.Feature):
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
        return 'read_dir'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="クライアント側でディレクトリ内の画像ファイルを取得します。",
            discription_en="Get image files in the directory on the client side.",
            test_assert="assert result != ''",
            choise=[
                dict(opt="glob_str", type="str", default=None, required=True, multi=False, hide=False, choise=None,
                        discription_ja="読込むファイルのglobパターンを指定します。",
                        discription_en="Specifies the glob pattern of the file to be read.",
                        test_true={"jpeg":"tests/*.jpg"}),
                dict(opt="read_input_type", type="str", default="jpeg", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture', 'filelist'],
                        discription_ja="読込む画像のタイプを指定します。",
                        discription_en="Specifies the type of image to be loaded.",
                        test_true={"jpeg":"jpeg",
                                "bmp":"bmp",
                                "png":"png",
                                "capture":"capture",
                                "filelist":"filelist"}),
                dict(opt="image_type", type="str", default="capture", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture'],
                        discription_ja="出力する画像のタイプを指定します。",
                        discription_en="Specify the type of image to output.",
                        test_true={"jpeg":"capture",
                                "bmp":"bmp",
                                "png":"png"}),
                dict(opt="root_dir", type="dir", default=None, required=True, multi=False, hide=False, choise=None,
                        discription_ja="検索の基準となるルートディレクトリを指定します。",
                        discription_en="Specifies the root directory on which to base the search.",
                        test_true={"jpeg":"."}),
                dict(opt="include_hidden", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="読込むファイルの種類に隠しファイルを含めるかどうかを指定します。",
                        discription_en="Specify whether to include hidden files in the types of files to be read.",
                        test_true={"jpeg":False,
                                "bmp":True}),
                dict(opt="moveto", type="dir", default=None, required=False, multi=False, hide=False, choise=None,
                        discription_ja="読み込んだファイルを移動する先のディレクトリを指定します。",
                        discription_en="Specifies the destination directory to which loaded files are to be moved."),
                dict(opt="polling", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="定期的にディレクトリ内の読込みを繰り返すかどうかを指定します。",
                        discription_en="Specifies whether to repeat reading in the directory periodically.",
                        test_true={"jpeg":True}),
                dict(opt="polling_count", type="int", default=10, required=False, multi=False, hide=True, choise=None,
                        discription_ja="ディレクトリ内の読込みの繰り返し回数を指定します。0以下の場合は無限に繰り返します。",
                        discription_en="Specifies the number of repeated readings in the directory.If it is less than or equal to 0, it repeats indefinitely.",
                        test_true={"jpeg":2}),
                dict(opt="polling_interval", type="int", default=1, required=False, multi=False, hide=True, choise=None,
                        discription_ja="ディレクトリ内の読込みの繰り返し間隔(秒)を指定します。",
                        discription_en="Specifies the repetition interval (in seconds) for reading in the directory.",
                        test_true={"jpeg":1}),
                dict(opt="output_csv", type="file", default="", required=False, multi=False, hide=True, choise=None, fileio="out",
                        discription_ja="入力した内容をcsvで保存します。これを指定した場合、標準出力は行いません。",
                        discription_en="Saves the input as a csv file. If this is specified, no standard output is performed.",
                        test_true={"jpeg":None,
                                "bmp":"read_dir.csv"}),
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

        root_dir = Path(args.root_dir) if args.root_dir is not None else Path('.')
        moveto = Path(args.moveto) if args.moveto is not None else None
        ret = None
        try:
            for t,b64,h,w,c,fn in cl.read_dir(args.glob_str, read_input_type=args.read_input_type, image_type=args.image_type,
                                              root_dir=root_dir, include_hidden=args.include_hidden, moveto=moveto,
                                              polling=args.polling, polling_count=args.polling_count, polling_interval=args.polling_interval):
                ret = f"{t},"+b64+f",{h},{w},{c},{fn}"
                if args.output_csv is not None:
                    with open(args.output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                        print(ret, file=f)
                        append = True
                else:
                    common.print_format(ret, False, tm, None, False)
        except Exception as e:
            msg = {"warn":f"{e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, cl

        return 0, ret, cl
