from beaker.middleware import SessionMiddleware
from iinfer.app import common, options
from iinfer.app.commons import convert, module
from pathlib import Path
from typing import Any, Dict, List
import ctypes
import bottle
import bottle_websocket
import cv2
import datetime
import gevent
import hashlib
import logging
import os
import requests
import queue
import signal
import sys
import threading
import traceback
import time
import webbrowser

class Web:
    def __init__(self, logger:logging.Logger, data:Path, redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server',
                 client_only:bool=False, gui_html:str=None, filer_html:str=None, showimg_html:str=None, webcap_html:str=None, anno_html:str=None,
                 assets:List[str]=None, signin_html:str=None, signin_file:str=None, gui_mode:bool=False):
        """
        iinferクライアント側のwebapiサービス

        Args:
            logger (logging): ロガー
            data (Path): コマンドやパイプラインの設定ファイルを保存するディレクトリ
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): 推論サーバーのサービス名. Defaults to 'server'.
            client_only (bool, optional): クライアントのみのサービスかどうか. Defaults to False.
            gui_html (str, optional): GUIのHTMLファイル. Defaults to None.
            filer_html (str, optional): ファイラーのHTMLファイル. Defaults to None.
            showimg_html (str, optional): 画像表示のHTMLファイル. Defaults to None.
            webcap_html (str, optional): ウェブカメラのHTMLファイル. Defaults to None.
            anno_html (str, optional): アノテーション画面のHTMLファイル. Defaults to None.
            assets (List[str], optional): 静的ファイルのリスト. Defaults to None.
            signin_html (str, optional): ログイン画面のHTMLファイル. Defaults to None.
            signin_file (str, optional): ログイン情報のファイル. Defaults to args.signin_file.
            gui_mode (bool, optional): GUIモードかどうか. Defaults to False.
        """
        super().__init__()
        self.logger = logger
        self.data = data
        self.container = dict()
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = svname
        self.client_only = client_only
        if self.client_only:
            self.svname = 'client'
        self.gui_html = Path(gui_html) if gui_html is not None else None
        self.filer_html = Path(filer_html) if filer_html is not None else None
        self.showimg_html = Path(showimg_html) if showimg_html is not None else None
        self.webcap_html = Path(webcap_html) if webcap_html is not None else None
        self.anno_html = Path(anno_html) if anno_html is not None else None
        self.assets = [Path(a) for a in assets] if assets is not None else None
        self.signin_html = Path(signin_html) if signin_html is not None else None
        self.signin_file = Path(signin_file) if signin_file is not None else None
        self.gui_html_data = None
        self.filer_html_data = None
        self.showimg_html_data = None
        self.webcap_html_data = None
        self.anno_html_data = None
        self.signin_html_data = None
        self.signin_file_data = None
        self.gui_mode = gui_mode
        self.cmds_path = self.data / ".cmds"
        self.pipes_path = self.data / ".pipes"
        self.static_root = Path(__file__).parent.parent / 'web'
        common.mkdirs(self.cmds_path)
        common.mkdirs(self.pipes_path)
        self.pipe_th = None
        self.img_queue = queue.Queue(1000)
        self.cb_queue = queue.Queue(1000)
        self.options = options.Options()
        #self.webcap_client = httpx.Client()
        self.webcap_client = requests.Session()
        self.logger.info(f"initialization parameter.")
        self.logger.info(f" redis_host={self.redis_host}")
        self.logger.info(f" redis_port={self.redis_port}")
        self.logger.info(f" redis_password=********")
        self.logger.info(f" svname={self.svname}")
        self.logger.info(f" data={self.data} -> {self.data.absolute()}")
        self.logger.info(f" client_only={self.client_only}")
        self.logger.info(f" gui_html={self.gui_html}")
        self.logger.info(f" filer_html={self.filer_html}")
        self.logger.info(f" showimg_html={self.showimg_html}")
        self.logger.info(f" webcap_html={self.webcap_html}")
        self.logger.info(f" anno_html={self.anno_html}")
        self.logger.info(f" assets={self.assets}")
        self.logger.info(f" signin_html={self.signin_html}")
        self.logger.info(f" signin_file={self.signin_file}")
        self.logger.info(f" gui_mode={self.gui_mode}")
        self.logger.info(f" cmds_path={self.cmds_path} -> {self.cmds_path.absolute()}")
        self.logger.info(f" pipes_path={self.pipes_path} -> {self.pipes_path.absolute()}")

    def load_signin_file(self):
        if self.signin_file is not None:
            if not self.signin_file.is_file():
                raise FileNotFoundError(f'signin_file is not found. ({self.signin_file})')
            with open(self.signin_file, 'r', encoding='utf-8') as f:
                self.signin_file_data = dict()
                for line in f:
                    if line.strip() == '': continue
                    parts = line.strip().split(':')
                    if len(parts) <= 2:
                        raise ValueError(f'signin_file format error. Format must be "userid:passwd:algname\\n". ({self.signin_file}). {line} split={parts} len={len(parts)}')
                    self.signin_file_data[parts[0]] = dict(password=parts[1], algname=parts[2])
                    if parts[2] not in ['plain', 'md5', 'sha1', 'sha256']:
                        raise ValueError(f'signin_file format error. Algorithms not supported. ({self.signin_file}). algname={parts[2]} "plain", "md5", "sha1", "sha256" only.')

    def check_signin(self) -> bool:
        """
        ログインチェック
        """
        if self.signin_file is None:
            return True
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        session = bottle.request.environ.get('beaker.session')
        if 'signin' in session:
            userid = session['signin']['userid']
            passwd = session['signin']['password']
            if userid in self.signin_file_data and passwd == self.signin_file_data[userid]['password']:
                session.save()
                return True
        self.logger.warning(f"signin error. session={session}")
        return False

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081, session_timeout:int=600, outputs_key:List[str]=[]):
        """
        Webサーバを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_port (int, optional): リスンポート. Defaults to 8081.
            session_timeout (int, optional): セッションタイムアウト. Defaults to 600.
            outputs_key (list, optional): 出力キー. Defaults to [].
        """
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.outputs_key = outputs_key
        self.session_timeout = session_timeout
        self.logger.info(f"start parameter.")
        self.logger.info(f" allow_host={self.allow_host}")
        self.logger.info(f" listen_port={self.listen_port}")
        self.logger.info(f" outputs_key={self.outputs_key}")

        app = bottle.Bottle()
        app_session = SessionMiddleware(app, {
            'session.type': 'memory',
            'session.timeout': self.session_timeout,
            'session.auto': True,
            'session.renew': True
        })
        if self.gui_html is not None:
            if not self.gui_html.is_file():
                raise FileNotFoundError(f'gui_html is not found. ({self.gui_html})')
            with open(self.gui_html, 'r', encoding='utf-8') as f:
                self.gui_html_data = f.read()
        if self.filer_html is not None:
            if not self.filer_html.is_file():
                raise FileNotFoundError(f'filer_html is not found. ({self.filer_html})')
            with open(self.filer_html, 'r', encoding='utf-8') as f:
                self.filer_html_data = f.read()
        if self.showimg_html is not None:
            if not self.showimg_html.is_file():
                raise FileNotFoundError(f'showimg_html is not found. ({self.showimg_html})')
            with open(self.showimg_html, 'r', encoding='utf-8') as f:
                self.showimg_html_data = f.read()
        if self.webcap_html is not None:
            if not self.webcap_html.is_file():
                raise FileNotFoundError(f'webcap_html is not found. ({self.webcap_html})')
            with open(self.webcap_html, 'r', encoding='utf-8') as f:
                self.webcap_html_data = f.read()
        if self.anno_html is not None:
            if not self.anno_html.is_file():
                raise FileNotFoundError(f'anno_html is not found. ({self.anno_html})')
            with open(self.anno_html, 'r', encoding='utf-8') as f:
                self.anno_html_data = f.read()
        if self.assets is not None:
            if type(self.assets) != list:
                raise TypeError(f'assets is not list. ({self.assets})')
            for i, asset in enumerate(self.assets):
                if not asset.is_file():
                    raise FileNotFoundError(f'asset is not found. ({asset})')
                with open(asset, 'r', encoding='utf-8') as f:
                    asset_data = f.read()
                    def asset_func(asset_data):
                        @app.route(f'/{asset.name}')
                        def func():
                            return asset_data
                        return func
                    asset_func(asset_data)
        self.load_signin_file()
        if self.signin_html is not None:
            if not self.signin_html.is_file():
                raise FileNotFoundError(f'signin_html is not found. ({self.signin_html})')
            with open(self.signin_html, 'r', encoding='utf-8') as f:
                self.signin_html_data = f.read()
        
        for wf in module.load_webfeatures("iinfer.app.features.web"):
            wf.route(self, app)

        @app.hook('after_request')
        def enable_cors():
            """
            CORSを有効にする
            """
            if not 'Origin' in bottle.request.headers.keys():
                return
            bottle.response.headers['Access-Control-Allow-Origin'] = bottle.request.headers['Origin']

        @app.route('/')
        def index():
            return bottle.redirect('gui')

        self.is_running = True
        server = _WSGIServer(host=self.allow_host, port=self.listen_port, gui_mode=self.gui_mode)
        th = RaiseThread(target=bottle.run, kwargs=dict(app=app_session, server=server))
        th.start()
        try:
            with open("iinfer_web.pid", mode="w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            while self.is_running:
                gevent.sleep(1)
            th.raise_exception()
        except KeyboardInterrupt:
            th.raise_exception()
        try:
            server.srv.shutdown()
        except:
            pass

    def stop(self):
        """
        Webサーバを停止する
        """
        try:
            with open("iinfer_web.pid", mode="r", encoding="utf-8") as f:
                pid = f.read()
                if pid != "":
                    os.kill(int(pid), signal.CTRL_C_EVENT)
                    self.logger.info(f"Stop bottle web. allow_host={self.allow_host} listen_port={self.listen_port}")
                else:
                    self.logger.warning(f"pid is empty.")
            Path("iinfer_web.pid").unlink(missing_ok=True)
        except:
            traceback.print_exc()

    def webcap(self, allow_host:str="0.0.0.0", listen_port:int=8082,
               image_type:str='capture', outputs_key:List[str]=None, capture_frame_width:int=None, capture_frame_height:int=None,
               capture_count:int=5, capture_fps:int=5):
        """
        Webキャプチャを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_port (int, optional): リスンポート. Defaults to 8082.
            image_type (str, optional): 画像タイプ. Defaults to 'capture'.
            outputs_key (list, optional): 出力キー. Defaults to None.
            capture_frame_width (int, optional): キャプチャフレーム幅. Defaults to None.
            capture_frame_height (int, optional): キャプチャフレーム高さ. Defaults to None.
            capture_count (int, optional): キャプチャ回数. Defaults to 5.
            capture_fps (int, optional): キャプチャFPS. Defaults to 5.
        """
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.image_type = image_type
        self.outputs_key = outputs_key
        self.capture_frame_width = capture_frame_width
        self.capture_frame_height = capture_frame_height
        self.capture_count = capture_count
        self.capture_fps = capture_fps
        self.count = 0
        self.logger.info(f"start webcap parameter.")
        self.logger.info(f" allow_host={self.allow_host}")
        self.logger.info(f" listen_port={self.listen_port}")
        self.logger.info(f" outputs_key={self.outputs_key}")
        self.logger.info(f" capture_frame_width={self.capture_frame_width}")
        self.logger.info(f" capture_frame_height={self.capture_frame_height}")
        self.logger.info(f" capture_count={self.capture_count}")
        self.logger.info(f" capture_fps={self.capture_fps}")

        app = bottle.Bottle()
        app_session = SessionMiddleware(app, {
            'session.type': 'memory',
            'session.cookie_expires': 600,
            'session.timeout': 600,
            'session.auto': True,
            'session.renew': True
        })
        self.load_signin_file()

        @app.route('/webcap/pub_img', method='POST')
        def pub_img_webcap():
            """
            webcap(プロキシ)から送信されてきた画像を、指定された画像タイプに変換して標準出力する
            """
            if self.logger.level == logging.DEBUG:
                self.logger.debug(f"web.pub_img_webcap: headers={dict(bottle.request.headers)}")
            if not bottle.request.content_type.startswith('multipart/form-data'):
                bottle.abort(400, 'Expected multipart request.')
                return
            bottle.response.headers['Access-Control-Allow-Origin'] = '*'

            image_type = self.image_type
            try:
                tm = time.perf_counter()
                for fn in bottle.request.files.keys():
                    cap:bytes = bottle.request.files[fn].file.read()
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
                    yield
                    gevent.sleep(10)
                    self.logger.info(f"Exit webcap. allow_host={self.allow_host} listen_port={self.listen_port}")
                    exit(0)

            except Exception as e:
                self.logger.warning('pub_img_webcap error', exc_info=True)
                return common.to_str(dict(warn=f'pub_img_webcap error. {traceback.format_exc()}'))

            ret = common.to_str(dict(success='pub_img_webcap to stdout.'))
            return ret

        self.is_running = True
        server = _WSGIServer(host=self.allow_host, port=self.listen_port, gui_mode=self.gui_mode, webcap=True)
        th = RaiseThread(target=bottle.run, kwargs=dict(app=app_session, server=server, host=allow_host, port=listen_port))
        th.start()
        try:
            tm = time.time()
            while self.is_running:
                if time.time() - tm > 15:
                    tm = time.time()
                    sys.stderr.write(f"webcap running. count={self.count}, capture_count={self.capture_count}\n")
                gevent.sleep(1)
            th.raise_exception()
        except KeyboardInterrupt:
            th.raise_exception()
        try:
            server.srv.shutdown()
        except:
            pass
        finally:
            self.logger.info(f"Exit webcap. allow_host={self.allow_host} listen_port={self.listen_port}")
            exit(0)

class _WSGIServer(bottle_websocket.GeventWebSocketServer):
#class _WSGIServer(bottle.WSGIRefServer):
    """
    runメソッドでWSGIRefServerを起動する際に、make_serverの戻り値をインスタンス変数にするためのクラス
    """
    def __init__(self, host='127.0.0.1', port:int=8080, gui_mode:bool=False, webcap:bool=False, **options):
        super().__init__(host, port, **options)
        self.gui_mode = gui_mode
        self.webcap = webcap

    def run(self, handler):
        import logging
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        from geventwebsocket.logging import create_logger

        # self.srvに代入することで、shutdownを実行できるようにする
        self.srv = pywsgi.WSGIServer((self.host, self.port), handler, handler_class=WebSocketHandler)

        if not self.quiet:
            self.srv.logger = create_logger('geventwebsocket.logging')
            self.srv.logger.setLevel(logging.INFO if not self.webcap else logging.NOTSET)
            self.srv.logger.addHandler(logging.StreamHandler())

        if self.webcap:
            sys.stderr.write(f"webcap ready.\n") # webcapのwebsocketの接続接続開始の合図
        if self.gui_mode:
            webbrowser.open(f'http://localhost:{self.port}/gui')
        self.srv.serve_forever()

class RaiseThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._run = self.run
        self.run = self.set_id_and_run

    def set_id_and_run(self):
        self.id = threading.get_native_id()
        self._run()

    def get_id(self):
        return self.id
        
    def raise_exception(self):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.get_id()), 
            ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.get_id()), 
                0
            )
            print('Failure in raising exception')
