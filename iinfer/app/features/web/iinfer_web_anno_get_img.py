from cmdbox.app import common
from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from iinfer import version
from iinfer.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import io


class AnnoGetImg(cmdbox_web_exec_cmd.ExecCmd):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/annotation/get_img/{constr}')
        async def anno_get_img(req:Request, res:Response, constr:str):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            try:
                host, port, svname, password, path, scope, img_thumbnail = convert.b64str2str(constr).split('\t')
                data_dir = web.data if scope == 'client' else Path.cwd()
                opt = dict(host=host, port=port, svname=svname, password=password, svpath=path, scope=scope,
                           img_thumbnail=img_thumbnail, mode='client', cmd='file_download', client_data=data_dir, stdout_log=False)
                opt['capture_stdout'] = nothread = True
                ret = self.exec_cmd(web, 'file_download', opt, nothread)
                if len(ret) == 0 or 'success' not in ret[0] or 'data' not in ret[0]['success']:
                    return common.to_str(ret)
                mime = ret[0]['success']['mime_type']
                return StreamingResponse(io.BytesIO(convert.b64str2bytes(ret[0]['success']['data'])),
                                         headers={'Cache-Control':'no-cache'},
                                         media_type=mime)
            except Exception as e:
                raise HTTPException(status_code=404, detail='Missing specified file or not an image.') from e
