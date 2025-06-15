from cmdbox.app import common, web
from cmdbox.app.commons import convert
from fastapi import FastAPI, Request, Response, HTTPException
from pathlib import Path
from starlette.datastructures import UploadFile
from starlette.responses import PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware
from typing import Any, Dict, List
from uvicorn.config import Config
import asyncio
import cv2
import datetime
import gevent
import logging
import sys
import traceback
import time
import uvicorn


class Web(web.Web):
    def __init__(self, logger:logging.Logger, data:Path, appcls=None, ver=None,
                 redis_host:str="localhost", redis_port:int = 6379, redis_password:str = None, svname:str='server',
                 client_only:bool=False, doc_root:Path=None, gui_html:str=None, filer_html:str=None, result_html:str=None, users_html:str=None,
                 audit_html:str=None, agent_html:str=None, assets:List[str]=None, signin_html:str=None, signin_file:str=None, gui_mode:bool=False,
                 web_features_packages:List[str]=None, web_features_prefix:List[str]=[],
                 showimg_html:str=None, webcap_html:str=None, anno_html:str=None):
        """
        iinferクライアント側のwebapiサービス

        Args:
            logger (logging): ロガー
            data (Path): コマンドやパイプラインの設定ファイルを保存するディレクトリ
            appcls ([type], optional): アプリケーションクラス. Defaults to None.
            ver ([type], optional): バージョン. Defaults to None.
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): 推論サーバーのサービス名. Defaults to 'server'.
            client_only (bool, optional): クライアントのみのサービスかどうか. Defaults to False.
            doc_root (Path, optional): カスタムファイルのドキュメントルート. フォルダ指定のカスタムファイルのパスから、doc_rootのパスを除去したパスでURLマッピングします。Defaults to None.
            gui_html (str, optional): GUIのHTMLファイル. Defaults to None.
            filer_html (str, optional): ファイラーのHTMLファイル. Defaults to None.
            result_html (str, optional): 結果表示のHTMLファイル. Defaults to None.
            users_html (str, optional): ユーザー管理のHTMLファイル. Defaults to None.
            audit_html (str, optional): 監査ログのHTMLファイル. Defaults to None.
            agent_html (str, optional): エージェント管理のHTMLファイル. Defaults to None.
            assets (List[str], optional): 静的ファイルのリスト. Defaults to None.
            signin_html (str, optional): ログイン画面のHTMLファイル. Defaults to None.
            signin_file (str, optional): ログイン情報のファイル. Defaults to args.signin_file.
            gui_mode (bool, optional): GUIモードかどうか. Defaults to False.
            web_features_packages (List[str], optional): webfeatureのパッケージ名のリスト. Defaults to None.
            web_features_prefix (List[str], optional): webfeatureのプレフィックスのリスト. Defaults to None.
            showimg_html (str, optional): 画像表示のHTMLファイル. Defaults to None.
            webcap_html (str, optional): ウェブカメラのHTMLファイル. Defaults to None.
            anno_html (str, optional): アノテーション画面のHTMLファイル. Defaults to None.
        """
        doc_root = doc_root if doc_root is not None else Path(__file__).parent.parent / 'web'
        assets = assets if assets is not None else [str(Path(__file__).parent.parent / 'web' / 'assets')]
        super().__init__(logger=logger, data=data, appcls=appcls, ver=ver,
                         redis_host=redis_host, redis_port=redis_port, redis_password=redis_password, svname=svname,
                         client_only=client_only, doc_root=doc_root, gui_html=gui_html, filer_html=filer_html,
                         result_html=result_html, users_html=users_html, audit_html=audit_html, agent_html=agent_html,
                         assets=assets, signin_html=signin_html, signin_file=signin_file, gui_mode=gui_mode,
                         web_features_packages=web_features_packages, web_features_prefix=web_features_prefix)

        self.showimg_html = Path(showimg_html) if showimg_html is not None else Path(__file__).parent.parent / 'web' / 'showimg.html'
        self.webcap_html = Path(webcap_html) if webcap_html is not None else Path(__file__).parent.parent / 'web' / 'webcap.html'
        self.anno_html = Path(anno_html) if anno_html is not None else Path(__file__).parent.parent / 'web' / 'annotation.html'

        self.showimg_html_data = None
        self.webcap_html_data = None
        self.anno_html_data = None
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web init parameter: showimg_html={self.showimg_html}")
            self.logger.debug(f"web init parameter: webcap_html={self.webcap_html}")
            self.logger.debug(f"web init parameter: anno_html={self.anno_html}")

    def webcap(self, allow_host:str="0.0.0.0", listen_webcap_port:int=8082,
               image_type:str='capture', outputs_key:List[str]=None, capture_frame_width:int=None, capture_frame_height:int=None,
               capture_count:int=5, capture_fps:int=5):
        """
        Webキャプチャを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_webcap_port (int, optional): リスンポート. Defaults to 8082.
            image_type (str, optional): 画像タイプ. Defaults to 'capture'.
            outputs_key (list, optional): 出力キー. Defaults to None.
            capture_frame_width (int, optional): キャプチャフレーム幅. Defaults to None.
            capture_frame_height (int, optional): キャプチャフレーム高さ. Defaults to None.
            capture_count (int, optional): キャプチャ回数. Defaults to 5.
            capture_fps (int, optional): キャプチャFPS. Defaults to 5.
        """
        self.allow_host = allow_host
        self.listen_webcap_port = listen_webcap_port
        self.image_type = image_type
        self.outputs_key = outputs_key
        self.capture_frame_width = capture_frame_width
        self.capture_frame_height = capture_frame_height
        self.capture_count = capture_count
        self.capture_fps = capture_fps
        self.count = 0
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web webcap parameter: allow_host={self.allow_host}")
            self.logger.debug(f"web webcap parameter: listen_webcap_port={self.listen_webcap_port}")
            self.logger.debug(f"web webcap parameter: image_type={self.image_type}")
            self.logger.debug(f"web webcap parameter: outputs_key={self.outputs_key}")
            self.logger.debug(f"web webcap parameter: capture_frame_width={self.capture_frame_width}")
            self.logger.debug(f"web webcap parameter: capture_frame_height={self.capture_frame_height}")
            self.logger.debug(f"web webcap parameter: capture_count={self.capture_count}")
            self.logger.debug(f"web webcap parameter: capture_fps={self.capture_fps}")

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key=common.random_string())
        self.init_webfeatures(app)

        @app.get('/webcap/pub_img', response_class=PlainTextResponse)
        async def pub_img_webcap_chk(req:Request, res:Response):
            return "ok"

        @app.post('/webcap/pub_img')
        async def pub_img_webcap(req:Request, res:Response, title:str=None):
            """
            webcap(プロキシ)から送信されてきた画像を、指定された画像タイプに変換して標準出力する
            """
            if self.logger.level == logging.DEBUG:
                self.logger.debug(f"web.pub_img_webcap: headers={dict(res.headers)}")
            content_type = req.headers.get('content-type')
            if content_type is None or not content_type.startswith('multipart/form-data'):
                raise HTTPException(status_code=400, detail='Expected multipart request.')
            res.headers['Access-Control-Allow-Origin'] = '*'

            image_type = self.image_type
            try:
                tm = time.perf_counter()
                form = await req.form()
                files = {key: value for key, value in form.items() if isinstance(value, UploadFile)}
                for fn in files.keys():
                    cap:bytes = files[fn].file.read()
                    if cap is None:
                        continue
                    output_image_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    cap = cap.decode().replace('data:image/jpeg;base64,','')
                    if self.logger.level == logging.DEBUG:
                        ret_str = common.to_str(cap, slise=100)
                        self.logger.debug(f"web.pub_img_webcap: cap={ret_str}")
                    img_npy = convert.imgbytes2npy(convert.b64str2bytes(cap))
                    if self.capture_frame_width is not None and self.capture_frame_height is not None:
                        img_npy = cv2.resize(img_npy, (self.capture_frame_width, self.capture_frame_height), interpolation=cv2.INTER_NEAREST)
                    img_b64 = None
                    if image_type == 'capture' or image_type is None:
                        image_type = 'capture'
                        img_b64 = convert.npy2b64str(img_npy)
                    else:
                        img_b64 = convert.bytes2b64str(convert.npy2imgfile(img_npy, image_type=image_type))
                    output_image_name = f"{output_image_name}.{image_type}"

                    t, b64, h, w, c, fn = image_type, img_b64, img_npy.shape[0], img_npy.shape[1], img_npy.shape[2] if len(img_npy.shape) > 2 else -1, output_image_name
                    ret = f"{t},"+b64+f",{h},{w},{c},{fn}"
                    if self.logger.level == logging.DEBUG:
                        ret_str = common.to_str(ret, slise=100)
                        self.logger.debug(f"web.pub_img_webcap: ret={ret_str}")
                    common.print_format(ret, False, tm, None, False)
                    tm = time.perf_counter()
                    self.count += 1
                if self.capture_count > 0 and self.count >= self.capture_count:
                    self.is_running = False
                    #gevent.sleep(3)
                    self.logger.info(f"Exit webcap. allow_host={self.allow_host} listen_webcap_port={self.listen_webcap_port}")

            except Exception as e:
                self.logger.warning('pub_img_webcap error', exc_info=True)
                return common.to_str(dict(warn=f'pub_img_webcap error. {traceback.format_exc()}'))

            ret = common.to_str(dict(success='pub_img_webcap to stdout.'))
            return ret

        self.is_running = True
        log_config = {"version":1,
                      "formatters":{
                            "fmt":{
                                "format":'%(levelname)s[%(asctime)s] - %(message)s',
                                "class":"logging.Formatter"}},
                      "handlers":{
                            "std":{
                                "class":"cmdbox.app.commons.loghandler.ColorfulStreamHandler",
                                "level":"NOTSET",
                                "formatter":"fmt",
                                "stream":"ext://sys.stdout"}},
                      "loggers":{
                            "uvicorn":{
                                "handlers":["std"],
                                "level":"NOTSET",
                                "qualname":"uvicorn"}}}

        class ThreadedUvicorn(web.ThreadedUvicorn):
            def __init__(self, logger:logging.Logger, config:Config):
                self.logger = logger
                self.server = uvicorn.Server(config)
                self.thread = web.RaiseThread(daemon=True, target=self.server.run)
            def start(self):
                self.thread.start()
                asyncio.run(self.wait_for_started())
            def stop(self):
                if self.thread.is_alive():
                    self.server.should_exit = True
                    self.thread.raise_exception()
                    while self.thread.is_alive():
                                time.sleep(0.1)
            def is_alive(self):
                return self.thread.is_alive()

        th = ThreadedUvicorn(self.logger, config=Config(app=app, host=self.allow_host, port=self.listen_webcap_port, log_config=log_config))
        th.start()
        try:
            tm = time.time()
            while self.is_running:
                if time.time() - tm > 15:
                    tm = time.time()
                    sys.stderr.write(f"webcap running. count={self.count}, capture_count={self.capture_count}\n")
                gevent.sleep(1)
            th.stop()
        except KeyboardInterrupt:
            th.stop()
