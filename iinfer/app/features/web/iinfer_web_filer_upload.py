from iinfer.app import common, web, feature
from iinfer.app.features.web import iinfer_web_exec_cmd
from pathlib import Path
import bottle
import tempfile


class FilerUpload(iinfer_web_exec_cmd.ExecCmd):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/filer/upload', method='POST')
        def filer_upload():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            return self.filer_upload(web, bottle.request)

    def filer_upload(self, web:web.Web, request:bottle.Request) -> str:
        """
        ファイルをアップロードする

        Args:
            web (web.Web): Webオブジェクト
            request (bottle.Request): リクエスト
        
        Returns:
            str: 結果
        """
        q = request.query
        svpath = q['svpath']
        web.logger.info(f"filer_upload: svpath={svpath}")
        opt = dict(mode='client', cmd='file_upload',
                   host=q['host'], port=q['port'], password=q['password'], svname=q['svname'],
                   scope=q["scope"], client_data=q['client_data'], orverwrite=('orverwrite' in q))
        for file in request.files.getall('files'):
            with tempfile.TemporaryDirectory() as tmpdir:
                raw_filename = file.raw_filename.replace('\\','/').replace('//','/')
                raw_filename = raw_filename if not raw_filename.startswith('/') else raw_filename[1:]
                upload_file:Path = Path(tmpdir) / raw_filename
                if not upload_file.parent.exists():
                    upload_file.parent.mkdir(parents=True)
                opt['svpath'] = str(svpath / Path(raw_filename).parent)
                opt['upload_file'] = str(upload_file).replace('"','')
                opt['capture_stdout'] = True
                file.save(opt['upload_file'])
                ret = self.exec_cmd(web, "file_upload", opt, nothread=True)
                if len(ret) == 0 or 'success' not in ret[0]:
                    return str(ret)
        return 'upload success'
        #return f'upload {upload.filename}'
