from cmdbox.app import common
from cmdbox.app.features.cli import cmdbox_web_start
from iinfer.app import web
from pathlib import Path
from typing import Dict, Any, Tuple, List
import argparse
import logging
import traceback


class WebStart(cmdbox_web_start.WebStart):
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt["choice"] += [
            dict(opt="showimg_html", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="`showimg.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                discription_en="Specify `showimg.html`. If omitted, the iinfer built-in HTML file is used."),
            dict(opt="webcap_html", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="`webcap.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                discription_en="Specify `webcap.html`. If omitted, the iinfer built-in HTML file is used."),
            dict(opt="anno_html", type="file", default=None, required=False, multi=False, hide=False, choice=None,
                discription_ja="`annotation.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                discription_en="Specify `annotation.html`. If omitted, the iinfer built-in HTML file is used."),
        ]
        return opt

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
            ssl_cert = None if args.ssl_cert is None else Path(args.ssl_cert)
            ssl_key = None if args.ssl_key is None else Path(args.ssl_key)
            ssl_ca_certs = None if args.ssl_ca_certs is None else Path(args.ssl_ca_certs)
            w = web.Web(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        client_only=args.client_only, doc_root=args.doc_root, gui_html=args.gui_html, filer_html=args.filer_html, assets=args.assets,
                        signin_html=args.signin_html, signin_file=args.signin_file, gui_mode=False,
                        showimg_html=args.showimg_html, webcap_html=args.webcap_html, anno_html=args.anno_html)
            w.start(args.allow_host, args.listen_port, ssl_listen_port=args.ssl_listen_port,
                    ssl_cert=ssl_cert, ssl_key=ssl_key, ssl_keypass=args.ssl_keypass, ssl_ca_certs=ssl_ca_certs,
                    session_timeout=args.session_timeout, outputs_key=args.outputs_key)

            msg = {"success":"web complate."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 0, msg, w
        except Exception as e:
            msg = {"warn":f"Web server start error. {traceback.format_exc()}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, w
