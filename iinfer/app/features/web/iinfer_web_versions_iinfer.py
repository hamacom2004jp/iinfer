from cmdbox.app import feature
from cmdbox.app.web import Web
from iinfer import version
from fastapi import FastAPI, Request, Response, HTTPException


class VersionsIinfer(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/versions_iinfer')
        async def versions_iinfer(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            logo = [version.__logo__]
            return logo + version.__description__.split('\n')
