from cmdbox.app import feature
from iinfer.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any


class Annotation(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.anno_html is not None:
            if not web.anno_html.is_file():
                raise FileNotFoundError(f'anno_html is not found. ({web.anno_html})')
            with open(web.anno_html, 'r', encoding='utf-8') as f:
                web.anno_html_data = f.read()

        @app.get('/annotation', response_class=HTMLResponse)
        @app.post('/annotation', response_class=HTMLResponse)
        async def annotation(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            web.options.audit_exec(req, res, web)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.anno_html_data

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
        return dict(annotation=dict(html='Annotation', href='annotation', target='_blank', css_class='dropdown-item'))
