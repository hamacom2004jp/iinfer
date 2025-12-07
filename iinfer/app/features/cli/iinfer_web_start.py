from cmdbox.app.features.cli import cmdbox_web_start
from cmdbox.app.options import Options
from iinfer.app import web
from pathlib import Path
from typing import Dict, Any, Tuple, List
from urllib.request import pathname2url
import argparse
import logging


class WebStart(cmdbox_web_start.WebStart):
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt["choice"] += [
            dict(opt="showimg_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                 description_ja="`showimg.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                 description_en="Specify `showimg.html`. If omitted, the iinfer built-in HTML file is used."),
            dict(opt="webcap_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                 description_ja="`webcap.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                 description_en="Specify `webcap.html`. If omitted, the iinfer built-in HTML file is used."),
            dict(opt="anno_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                 description_ja="`annotation.html` を指定します。省略時はiinfer内蔵のHTMLファイルを使用します。",
                 description_en="Specify `annotation.html`. If omitted, the iinfer built-in HTML file is used."),
        ]
        return opt

    def createWeb(self, logger:logging.Logger, args:argparse.Namespace) -> web.Web:
        """
        Webオブジェクトを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            web.Web: Webオブジェクト
        """
        w = web.Web.getInstance(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                    redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                    client_only=args.client_only, doc_root=args.doc_root, gui_html=args.gui_html, filer_html=args.filer_html,
                    result_html=args.result_html, users_html=args.users_html,
                    showimg_html=args.showimg_html, webcap_html=args.webcap_html, anno_html=args.anno_html,
                    assets=args.assets, signin_html=args.signin_html, signin_file=args.signin_file, gui_mode=args.gui_mode)
        return w

    def start(self, w:web.Web, logger:logging.Logger, args:argparse.Namespace) -> None:
        """
        Webモードを起動します

        Args:
            w (web.Web): Webオブジェクト
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
        """
        w.start(allow_host=args.allow_host, listen_port=args.listen_port, ssl_listen_port=args.ssl_listen_port,
                ssl_cert=args.ssl_cert, ssl_key=args.ssl_key, ssl_keypass=args.ssl_keypass, ssl_ca_certs=args.ssl_ca_certs,
                session_domain=args.session_domain, session_path=args.session_path,
                session_secure=args.session_secure, session_timeout=args.session_timeout,
                outputs_key=args.outputs_key, gunicorn_workers=args.gunicorn_workers, gunicorn_timeout=args.gunicorn_timeout)