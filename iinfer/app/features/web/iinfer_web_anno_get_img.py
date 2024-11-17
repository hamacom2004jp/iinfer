from iinfer.app import common, web, feature
from iinfer.app.commons import convert
from iinfer.app.features.web import iinfer_web_exec_cmd
from pathlib import Path
import bottle


class AnnoGetImg(iinfer_web_exec_cmd.ExecCmd):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/annotation/get_img/<constr>')
        def anno_get_img(constr:str):
            if not web.check_signin():
                return bottle.redirect(f'/signin/annotation/get_img/{constr}')
            try:
                host, port, svname, password, path, scope, img_thumbnail = convert.b64str2str(constr).split('\t')
                data_dir = web.data if scope == 'client' else Path.cwd()
                opt = dict(host=host, port=port, svname=svname, password=password, svpath=path, scope=scope,
                           img_thumbnail=img_thumbnail, mode='client', cmd='file_download', client_data=data_dir, stdout_log=False)
                opt['capture_stdout'] = nothread = True
                ret = self.exec_cmd(web, 'file_download', opt, nothread)
                if len(ret) == 0 or 'success' not in ret[0] or 'data' not in ret[0]['success']:
                    return common.to_str(ret)
                bottle.response.content_type = ret[0]['success']['mime_type']
                bottle.response.headers['Cache-Control'] = f'no-cache'
                return convert.b64str2bytes(ret[0]['success']['data'])
            except Exception as e:
                web.logger.warning(f'Missing specified file or not an image {e}')
                bottle.abort(404, 'Missing specified file or not an image.')
                return
