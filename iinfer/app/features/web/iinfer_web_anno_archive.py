from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from iinfer.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from pathlib import Path
import tempfile
import traceback
import zipfile


class AnnoArchive(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/annotation/archive/{constr}')
        async def anno_archive(req:Request, res:Response, constr:str):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            try:
                host, port, svname, password, output_path, scope, img_thumbnail = convert.b64str2str(constr).split('\t')
                output_path = output_path[1:] if output_path.startswith('/') else output_path
                form = await req.form()
                archives = await req.json()
                data_dir = web.data if scope == 'client' else Path.cwd()
                opt = dict(host=host, port=port, svname=svname, password=password, scope=scope,
                            img_thumbnail=img_thumbnail, mode='client', cmd='file_download', client_data=data_dir, stdout_log=False)
                opt['capture_stdout'] = nothread = True
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir_path = Path(tmpdir)
                    for arc in archives:
                        opt['svpath'] = arc
                        ret = self.exec_cmd(req, res, web, 'file_download', opt, nothread, self.appcls)
                        if len(ret) == 0 or 'success' not in ret[0]:
                            return ret
                        arc = arc[1:] if arc.startswith('/') else arc
                        p:Path = Path(tmpdir_path / arc)
                        if not p.parent.exists():
                            p.parent.mkdir(parents=True)
                        with open(p, 'wb') as f:
                            f.write(convert.b64str2bytes(ret[0]['success']['data']))

                    upload_file:Path = tmpdir_path / output_path
                    if not str(upload_file).startswith(str(tmpdir_path)):
                        web.logger.warning(f'Invalid output path. {output_path}')
                        return dict(warn=f'Invalid output path. {output_path}')
                    with zipfile.ZipFile(upload_file, 'w') as zipf:
                        dir = str(Path(output_path).parent).replace('\\', '/') + '/'
                        for arc in archives:
                            arc = arc[1:] if arc.startswith('/') else arc
                            zipf.write(tmpdir_path / arc, arc.replace(dir, ''))

                    opt['cmd'] = 'file_upload'
                    opt['svpath'] = output_path
                    opt['orverwrite'] = True
                    opt['upload_file'] = str(upload_file).replace('"','')
                    web.options.audit_exec(req, res, web)
                    ret = self.exec_cmd(req, res, web, "file_upload", opt, nothread=True, appcls=self.appcls)
                    if len(ret) == 0 or 'success' not in ret[0]:
                        return ret
                    return ret
            except Exception as e:
                web.logger.warning(f'anno_archive error {e}')
                return dict(warn=f'anno_archive error. {traceback.format_exc()}')
