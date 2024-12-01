from cmdbox.app import feature
from cmdbox.app.web import Web
from iinfer import version
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse


class PubImgProxyChk(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/webcap/pub_img/{port:int}', response_class=PlainTextResponse)
        async def pub_img_proxy_chk(req:Request, res:Response, port:int):
            """
            webcapプロセスが起動しているか確認する

            Args:
                req (Request): リクエスト
                res (Response): レスポンス
                port (int): webcapプロセスのポート番号

            Returns:
                str: 起動している場合は`ok`、起動していない場合は`ng`
            """
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            try:
                # 事前に接続テストすることで、keepaliveを有効にしておく（画像送信時のTCP接続が高速化できる）
                responce = web.webcap_client.get(f'http://localhost:{port}/webcap/pub_img')
                if responce.status_code != 200:
                    return "ng"
                return "ok"
            except:
                return "ng"
