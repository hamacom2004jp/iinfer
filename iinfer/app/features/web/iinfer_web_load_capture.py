from cmdbox.app import feature
from cmdbox.app.commons import convert
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import List, Dict, Any
from pathlib import Path
import logging


class LoadCapture(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/load_capture')
        async def load_capture(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            current_path = form.get('current_path')
            ret = self.load_capture(web, current_path)
            web.options.audit_exec(req, res, web)
            return ret

    def load_capture(self, web:Web, current_path:str) -> List[Dict[str, Any]]:
        """
        キャプチャファイルを読み込む

        Args:
            web (Web): Webオブジェクト
            current_path (str): カレントパス

        Returns:
            list[Dict[str, Any]]: キャプチャファイルの内容
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_capture: current_path={current_path}")
        current_path:Path = Path(current_path)
        if not current_path.is_file():
            return {'warn': f'A non-file was selected.: {current_path}'}
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                ret = []
                for line in f:
                    cel = line.split(',')
                    res_json = dict(success=dict(image_name=cel[5]),
                                    output_image=None,
                                    output_image_shape=(int(cel[2]),int(cel[3]),int(cel[4])),
                                    output_image_name=cel[5])
                    if cel[0] == 'capture':
                        img_npy = convert.b64str2npy(cel[1], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='jpeg')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                    else:
                        res_json["output_image"] = cel[1]
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
        return dict(open_capture=dict(html='Open capture<input type="hidden" id="open_capture_path" value=""/>',
                                      href='#', target='', css_class='dropdown-item',
                                      onclick='open_capture_func(`open_capture_path`)'))
