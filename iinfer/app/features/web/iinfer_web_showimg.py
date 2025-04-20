from cmdbox.app import feature
from iinfer.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any


class Showimg(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.showimg_html is not None:
            if not web.showimg_html.is_file():
                raise FileNotFoundError(f'showimg_html is not found. ({web.showimg_html})')
            with open(web.showimg_html, 'r', encoding='utf-8') as f:
                web.showimg_html_data = f.read()

        @app.get('/showimg', response_class=HTMLResponse)
        @app.post('/showimg', response_class=HTMLResponse)
        def showimg(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            web.options.audit_exec(req, res, web)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.showimg_html_data

    def toolmenu(self, web:Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: ツールメニュー情報
        
        Sample:
            {
                'filer': {
                    'html': 'Filer',
                    'href': 'filer',
                    'target': '_blank',
                    'css_class': 'dropdown-item'
                    'onclick': 'alert("filer")'
                }
            }
        """
        return dict(showimg=dict(html='ShowImage', href='showimg', target='_blank', css_class='dropdown-item'))
