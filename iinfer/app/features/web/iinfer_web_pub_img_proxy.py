from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from starlette.datastructures import UploadFile
import logging
import io
import time


class PubImgProxy(feature.WebFeature):
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
            webcapプロセスからのレスポンスをそのまま返却する
            webcapプロセスが起動していない場合は502エラーを返却する

            Args:
                req (Request): リクエスト
                res (Response): レスポンス
                port (int): webcapプロセスのポート番号
            """
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.pub_img_proxy: target=http://localhost:{port}/webcap/pub_img, header={req.headers}")
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
                    web.logger.debug(f"web.pub_img_proxy: target=http://localhost:{port}/webcap/pub_img, res_status={responce.status_code}, tm={time.perf_counter()-tm:.3f}s")
                responce.headers.pop('server', None)
                return StreamingResponse(io.BytesIO(content), status_code=responce.status_code,
                                         headers=responce.headers, media_type=responce.headers.get('content-type'))
            except Exception as e:
                raise HTTPException(status_code=502, detail=f'web.start.pub_img_proxy: pub_img_proxy closed. {e}') from e
