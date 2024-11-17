from iinfer.app import app, common, web as _web, options
from iinfer.app.commons import convert
from iinfer.app.features.web import iinfer_web_load_cmd
from typing import Dict, Any, List
import bottle
import html
import io
import json
import traceback
import sys


class ExecCmd(iinfer_web_load_cmd.LoadCmd):
    def __init__(self):
        super().__init__()
    
    def route(self, web:_web.Web, app:bottle.Bottle) -> None:
        @app.route('/exec_cmd', method='POST')
        @app.route('/exec_cmd/<title>')
        @app.route('/exec_cmd/<title>', method='POST')
        def exec_cmd(title=None):
            try:
                if not web.check_signin():
                    return common.to_str(dict(warn=f'Command "{title}" failed. Please log in to retrieve session.'))
                opt = None
                if bottle.request.content_type.startswith('multipart/form-data'):
                    opt = self.load_cmd(web, title)
                    for fn in bottle.request.files.keys():
                        opt[fn] = bottle.request.files[fn].file
                        if fn == 'input_file': opt['stdin'] = False
                elif bottle.request.content_type.startswith('application/json'):
                    opt = bottle.request.json
                else:
                    opt = self.load_cmd(web, title)
                opt['capture_stdout'] = nothread = True
                opt['stdout_log'] = False
                return common.to_str(self.exec_cmd(web, title, opt, nothread))
            except:
                return common.to_str(dict(warn=f'Command "{title}" failed. {traceback.format_exc()}'))

    def chk_client_only(self, web:_web.Web, opt):
        """
        クライアントのみのサービスかどうかをチェックする

        Args:
            web (web.Web): Webオブジェクト
            opt (dict): オプション

        Returns:
            tuple: (クライアントのみ場合はTrue, メッセージ)
        """
        if not web.client_only:
            return False, None
        use_redis = web.options.get_cmd_attr(opt['mode'], opt['cmd'], "use_redis")
        if use_redis == self.USE_REDIS_FALSE:
            return False, None
        output = dict(warn=f'Commands that require a connection to the iinfer server are not available.'
                        +f' (mode={opt["mode"]}, cmd={opt["cmd"]}) '
                        +f'The cause is that the client_only option is specified when starting web mode.')
        if use_redis == self.USE_REDIS_TRUE:
            return True, output
        for c in web.options.get_cmd_attr(opt['mode'], opt['cmd'], "choise"):
            if c['opt'] == 'client_data' and 'client_data' in opt and opt['client_data'] is None:
                return True, output
        return False, None

    def exec_cmd(self, web:_web.Web, title:str, opt:Dict[str, Any], nothread:bool=False) -> List[Dict[str, Any]]:
        """
        コマンドを実行する

        Args:
            title (str): タイトル
            opt (dict): オプション
            nothread (bool, optional): スレッドを使わないかどうか. Defaults to False.
        
        Returns:
            list: コマンド実行結果
        """
        web.container['iinfer_app'] = app.IinferApp()
        def _exec_cmd(iinfer_app:app.IinferApp, title, opt, nothread=False):
            web.logger.info(f"exec_cmd: title={title}, opt={opt}")
            ret, output = self.chk_client_only(web, opt)
            if ret:
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return

            opt_list, file_dict = web.options.mk_opt_list(opt)
            old_stdout = sys.stdout

            if 'capture_stdout' in opt and opt['capture_stdout'] and 'stdin' in opt and opt['stdin']:
                output = dict(warn=f'The "stdin" and "capture_stdout" options cannot be enabled at the same time. This is because it may cause a memory squeeze.')
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return
            if 'capture_stdout' in opt and opt['capture_stdout']:
                sys.stdout = captured_output = io.StringIO()
            try:
                iinfer_app.main(args_list=opt_list, file_dict=file_dict, webcall=True)
                web.logger.disabled = False # ログ出力を有効にする
                capture_maxsize = opt['capture_maxsize'] if 'capture_maxsize' in opt else options.Options.DEFAULT_CAPTURE_MAXSIZE
                if 'capture_stdout' in opt and opt['capture_stdout']:
                    output = captured_output.getvalue().strip()
                    output_size = len(output)
                    if output_size > capture_maxsize:
                        o = output.split('\n')
                        if len(o) > 0:
                            osize = len(o[0])
                            oidx = int(capture_maxsize / osize)
                            if oidx > 0:
                                output = '\n'.join(o[-oidx:])
                            else:
                                output = [dict(warn=f'The captured stdout was discarded because its size was larger than {capture_maxsize} bytes.')]
                        else:
                            output = [dict(warn=f'The captured stdout was discarded because its size was larger than {capture_maxsize} bytes.')]
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                web.logger.disabled = False # ログ出力を有効にする
                web.logger.info(f'exec_cmd error. {traceback.format_exc()}')
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            sys.stdout = old_stdout
            if 'stdout_log' in opt and opt['stdout_log']:
                self.callback_console_modal_log_func(web, output)
            try:
                def to_json(o):
                    res_json = json.loads(o)
                    if 'output_image' in res_json and 'output_image_shape' in res_json:
                        img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='png')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                    return res_json
                try:
                    ret = [to_json(o) for o in output.split('\n') if o.strip() != '']
                except:
                    try:
                        ret = to_json(output)
                    except:
                        ret = output
                if nothread:
                    return ret
                self.callback_return_cmd_exec_func(web, title, ret)
            except:
                web.logger.warning(f'exec_cmd error.', exec_info=True)
                if nothread:
                    return output
                self.callback_return_cmd_exec_func(web, title, output)
        if nothread:
            return _exec_cmd(web.container['iinfer_app'], title, opt, True)
        th = _web.RaiseThread(target=_exec_cmd, args=(web.container['iinfer_app'], title, opt, False))
        th.start()
        return [dict(warn='start_cmd')]

