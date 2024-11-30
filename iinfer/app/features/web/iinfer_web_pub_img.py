from cmdbox.app import feature
from iinfer import version
from iinfer.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException, UploadFile
import logging
import time
import traceback


class PubImg(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/showimg/pub_img')
        async def pub_img(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            if req.headers.get('content-type').startswith('multipart/form-data'):
                raise HTTPException(status_code=400, detail='Expected multipart request.')
            try:
                tm = time.time()
                form = await req.form()
                files = {key: value for key, value in form.items() if isinstance(value, UploadFile)}
                for fn in files:
                    filename = files[fn].filename
                    web.img_queue.put((filename, files[fn].file.read()))
                    if web.logger.level == logging.DEBUG:
                        web.logger.debug(f"web.pub_img: filename={filename}")
                return dict(success='Added to queue.')
            except:
                web.logger.warning('pub_img error', exc_info=True)
                return dict(warn=f'pub_img error. {traceback.format_exc()}')
