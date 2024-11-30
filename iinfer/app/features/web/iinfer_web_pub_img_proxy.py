from cmdbox.app import common, feature
from cmdbox.app.web import Web
from iinfer import version
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from starlette.datastructures import UploadFile
import logging
import io
import time


class PubImgProxy(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/webcap/pub_img/{port:int}')
        async def pub_img_proxy(req:Request, res:Response, port:int):
            """
            webcap画面から送信されてくる画像を、webcapプロセスに送信(プロキシ)する
            """
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.pub_img_proxy: port=http://localhost:{port}/webcap/pub_img, headers={dict(req.headers)}")
            if not req.headers.get('content-type').startswith('multipart/form-data'):
                raise HTTPException(status_code=400, detail='Expected multipart request.')
            try:
                tm = time.perf_counter()
                form = await req.form()
                files = [['files', (fn, await form[fn].read(), form[fn].content_type)] for fn in form.keys() if isinstance(form[fn], UploadFile)]
                responce = web.webcap_client.post(f'http://localhost:{port}/webcap/pub_img', files=files)
                content = responce.content
                if web.logger.level == logging.DEBUG:
                    output_str = common.to_str(content.decode("utf-8"), slise=100)
                    web.logger.debug(f"web.pub_img_proxy: res_status={responce.status_code}, res_headers={responce.headers}, res_content={output_str}")
                return StreamingResponse(io.BytesIO(content), status_code=responce.status_code,
                                         headers=responce.headers, media_type=responce.headers.get('content-type'))
            except Exception as e:
                raise HTTPException(status_code=502, detail=f'web.start.pub_img_proxy: pub_img_proxy closed. {e}') from e
