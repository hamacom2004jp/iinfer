from iinfer.app import common, web, feature
from iinfer.app.commons import convert
from pathlib import Path
import bottle
import tempfile
import traceback
import zipfile


class AnnoArchive(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/annotation/archive/<constr>', method='POST')
        def anno_archive(constr:str):
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            try:
                host, port, svname, password, output_path, scope, img_thumbnail = convert.b64str2str(constr).split('\t')
                output_path = output_path[1:] if output_path.startswith('/') else output_path
                archives = bottle.request.json
                data_dir = web.data if scope == 'client' else Path.cwd()
                opt = dict(host=host, port=port, svname=svname, password=password, scope=scope,
                            img_thumbnail=img_thumbnail, mode='client', cmd='file_download', client_data=data_dir, stdout_log=False)
                opt['capture_stdout'] = nothread = True
                with tempfile.TemporaryDirectory() as tmpdir:
                    tmpdir_path = Path(tmpdir)
                    for arc in archives:
                        opt['svpath'] = arc
                        ret = web.exec_cmd('file_download', opt, nothread)
                        if len(ret) == 0 or 'success' not in ret[0]:
                            return common.to_str(ret)
                        arc = arc[1:] if arc.startswith('/') else arc
                        p:Path = Path(tmpdir_path / arc)
                        if not p.parent.exists():
                            p.parent.mkdir(parents=True)
                        with open(p, 'wb') as f:
                            f.write(convert.b64str2bytes(ret[0]['success']['data']))

                    upload_file:Path = tmpdir_path / output_path
                    if not str(upload_file).startswith(str(tmpdir_path)):
                        web.logger.warning(f'Invalid output path. {output_path}')
                        return common.to_str(dict(warn=f'Invalid output path. {output_path}'))
                    with zipfile.ZipFile(upload_file, 'w') as zipf:
                        dir = str(Path(output_path).parent).replace('\\', '/') + '/'
                        for arc in archives:
                            arc = arc[1:] if arc.startswith('/') else arc
                            zipf.write(tmpdir_path / arc, arc.replace(dir, ''))

                    opt['cmd'] = 'file_upload'
                    opt['svpath'] = output_path
                    opt['orverwrite'] = True
                    opt['upload_file'] = str(upload_file).replace('"','')
                    ret = web.exec_cmd("file_upload", opt, nothread=True)
                    if len(ret) == 0 or 'success' not in ret[0]:
                        return str(ret)
                    return str(ret)
            except Exception as e:
                web.logger.warning(f'anno_archive error {e}')
                return common.to_str(dict(warn=f'anno_archive error. {traceback.format_exc()}'))
