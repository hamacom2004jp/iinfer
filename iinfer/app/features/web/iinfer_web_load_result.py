from cmdbox.app import feature
from cmdbox.app.commons import convert
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import List, Dict, Any
from pathlib import Path
import logging
import json


class LoadResult(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/load_result')
        async def load_result(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            current_path = form.get('current_path')
            ret = self.load_result(web, current_path)
            web.options.audit_exec(req, res, web)
            return ret

    def load_result(self, web:Web, current_path:str) -> List[Dict[str, Any]]:
        """
        結果ファイルを読み込む

        Args:
            web (Web): Webオブジェクト
            current_path (str): カレントパス
        
        Returns:
            list[Dict[str, Any]]: 結果ファイルの内容
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_result: current_path={current_path}")
        current_path = Path(current_path)
        if not current_path.is_file():
            return {'warn': f'A non-file was selected.: {current_path}'}
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                ret = []
                for line in f:
                    res_json = json.loads(line)
                    if 'output_image' in res_json and 'output_image_shape' in res_json:
                        img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='jpeg')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                    ret.append(res_json)
                return ret
        except:
            return {'warn': f'An error occurred while reading the file.: {current_path}'}


    def filemenu(self, web:Web) -> Dict[str, Any]:
        """
        ファイルメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: fileメニュー情報
        
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
        return dict(open_output_json=dict(html='Open output_json<input type="hidden" id="open_output_json_path" value=""/>',
                                          href='#', target='', css_class='dropdown-item',
                                          onclick='open_output_json_func(`open_output_json_path`)'))
