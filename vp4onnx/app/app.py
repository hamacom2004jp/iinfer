from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from vp4onnx import version
from vp4onnx.app import common
from vp4onnx.app.processes import predict
from pathlib import Path
import eel
import random
import socket
import time


def is_port_in_use(port: int) -> bool:
      """
      ローカルマシンで指定されたポートが既に使用されているかどうかを確認します。

      Args:
            port (int): 確認するポート番号。

      Returns:
            bool: ポートが使用されている場合はTrue、それ以外の場合はFalse。
      """
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

def main(data_dir:Path,  boot_mode:str, boot_schema:str, boot_host:str, boot_port:int):
      """
      アプリケーションのメイン関数です。

      Args:
            data_dir (Path): アプリケーションのデータディレクトリのパス。
            boot_mode (str): 起動モード。
            boot_schema (str): ブートURLのスキーマ。
            boot_host (str): ブートURLのホスト。
            boot_port (int): ブートURLのポート番号。
      """
      logger, config = common.load_config()
      common.CONFIG = config
      common.LOGGER = logger
      common.APP_DATA_DIR = data_dir


      logger.info(f"Starting webapi..")
      app = FastAPI(
            title=f"{version.__title__} webapi",
            description="{version.__title__} by FastAPI.",
            version=version.__version__
      )

      @app.middleware("http")
      async def add_process_header(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            common.set_responce_header(response)
            return response

      app.mount("/web", StaticFiles(directory="vp4onnx/web", html=True), name="web")

      @app.get("/", response_class=HTMLResponse)
      def root():
            return """
            <!DOCTYPE html>
            <html dir="ltr" lang="ja"><head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <meta http-equiv="refresh" content="0;URL='/web'" />
            <title>Loading..</title>
            </head><body></body></html>
            """
      @app.get("/api")
      def api():
            return common.make_result({
                  "title":f"{version.__title__} webapi",
                  "description":f"{version.__title__} by FastAPI.",
                  "version":version.__version__
            })

      app.include_router(predict.router)

      logger.info(f"Started webapi.")

      if boot_mode == 'gui':
            logger.info(f"Started gui.")
            @eel.expose
            def get_booturl():
                  return f"{boot_schema}://{boot_host}:{boot_port}/index.html"

            eel.init("vp4onnx/web")

            eel_port = 20000
            while is_port_in_use(eel_port):
                  eel_port = random.randint(20001, 30000)

            eel.start("/boot.html", size=(480, 320), port=eel_port)
