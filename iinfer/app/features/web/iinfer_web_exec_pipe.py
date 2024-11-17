from iinfer.app import common, web as _web, options
from iinfer.app.commons import convert
from iinfer.app.features.web import iinfer_web_load_pipe, iinfer_web_raw_pipe
from pathlib import Path
from typing import Dict, Any, List
import bottle
import gevent
import html
import json
import subprocess
import os
import tempfile
import traceback


class ExecPipe(iinfer_web_load_pipe.LoadPipe, iinfer_web_raw_pipe.RawPipe):
    def __init__(self):
        super().__init__()
    
    def route(self, web:_web.Web, app:bottle.Bottle) -> None:
        @app.route('/exec_pipe/<title>')
        @app.route('/exec_pipe/<title>', method='POST')
        def exec_pipe(title):
            upfiles = dict()
            try:
                if not web.check_signin():
                    return common.to_str(dict(warn=f'Pipeline "{title}" failed. Please log in to retrieve session.'))
                opt = None
                if bottle.request.content_type.startswith('multipart/form-data'):
                    opt = self.load_pipe(web, title)
                    opt['request_files'] = dict()
                    for cmd_title in opt['pipe_cmd']:
                        if cmd_title == '':
                            continue
                        cmd_opt = self.load_cmd(web, cmd_title)
                        for fn in bottle.request.files.keys():
                            if fn in cmd_opt:
                                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(bottle.request.files[fn].filename).suffix) as tf:
                                    upfiles[fn] = tf.name
                                    tf.write(bottle.request.files[fn].file.read())
                                    tf.flush()
                                    opt['request_files'][fn] = tf.name
                                    if fn == 'input_file': opt['request_files']['stdin'] = False
                elif bottle.request.content_type.startswith('application/json'):
                    opt = bottle.request.json
                else:
                    opt = self.load_pipe(web, title)
                opt['capture_stdout'] = nothread = False
                opt['stdout_log'] = False
                return common.to_str(self.exec_pipe(web, title, opt, nothread))
            except:
                return common.to_str(dict(warn=f'Pipeline "{title}" failed. {traceback.format_exc()}'))
            finally:
                for tfname in upfiles.values():
                    os.unlink(tfname)

    def exec_pipe(self, web:_web.Web, title:str, opt:Dict[str, Any], nothread:bool=False, capture_stdin:bool=False) -> List[Dict[str, Any]]:
        """
        パイプラインを実行する

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            opt (dict): オプション
            nothread (bool, optional): スレッドを使わないかどうか. Defaults to False.
            capture_stdin (bool, optional): 標準入力をキャプチャするかどうか. Defaults to False.
        
        Returns:
            list: パイプライン実行結果
        """
        web.logger.info(f"exec_pipe: title={title}, opt={opt}")
        def to_json(o):
            res_json = json.loads(o)
            if 'output_image' in res_json and 'output_image_shape' in res_json:
                img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                img_bytes = convert.npy2imgfile(img_npy, image_type='png')
                res_json["output_image"] = convert.bytes2b64str(img_bytes)
            return res_json
        def _exec_pipe(title, opt, container, nothread=False, capture_stdin=False):
            capture_stdout = True
            for i, cmd_title in enumerate(opt['pipe_cmd']):
                if cmd_title == '':
                    continue
                cmd_opt = self.load_cmd(web, cmd_title)
                #cmd_ref = self.options.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd'])
                #chk_stdin = len([ref for ref in cmd_ref if ref['opt'] == 'stdin']) > 0
                #chk_input_file = len([ref for ref in cmd_ref if ref['opt'] == 'input_file']) > 0
                if 'capture_stdout' in cmd_opt:
                    capture_stdout = cmd_opt['capture_stdout']
                else:
                    capture_stdout = True
                if 'output_csv' in cmd_opt and cmd_opt['output_csv'] != '':
                    output = dict(warn=f'The "output_csv" option is not supported in pipe. ({cmd_title})')
                    self.callback_return_pipe_exec_func(web, title, output)
                    return
            cmdline = None
            has_warn = False
            for cl in self.raw_pipe(web, title, opt):
                if cl['type'] == 'cmdline':
                    cmdline = cl['raw']
                if cl['type'] == 'warn':
                    self.callback_return_pipe_exec_func(web, title, cl)
                    has_warn = True
            if cmdline is None:
                self.callback_return_pipe_exec_func(web, title, dict(warn='No command to execute.'))
                has_warn = True
            if has_warn: return
            try:
                container['pipe_proc'] = subprocess.Popen(cmdline, shell=True, text=True, encoding='utf-8',
                                                        stdin=(subprocess.PIPE if capture_stdin else None),
                                                        stdout=(subprocess.PIPE if capture_stdout else None),
                                                        stderr=(subprocess.STDOUT if capture_stdout else None))
                output = ""
                output_size = 0
                while container['pipe_proc'].poll() is None:
                    gevent.sleep(0.1)
                    if capture_stdout:
                        o = container['pipe_proc'].stdout.readline().strip()
                        if 0 >= len(o):
                            continue
                        try:
                            if len(o) < options.Options.DEFAULT_CAPTURE_MAXSIZE:
                                try:
                                    o = to_json(o)
                                except:
                                    pass
                                self.callback_return_stream_log_func(web, o)
                            else:
                                o = [dict(warn=f'The captured stdout was discarded because its size was larger than {options.Options.DEFAULT_CAPTURE_MAXSIZE} bytes.')]
                                self.callback_return_stream_log_func(web, o)
                        except:
                            o = [dict(warn=f'<pre>{html.escape(o)}</pre><br><pre>{html.escape(traceback.format_exc())}</pre>')]
                            self.callback_return_stream_log_func(web, o)
                if capture_stdout:
                    container['pipe_proc'].stdout.read() # 最後のストリームは読み捨て
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            if 'stdout_log' in opt and cmd_opt['stdout_log']:
                self.callback_console_modal_log_func(web, output)
            try:
                try:
                    ret = [to_json(o) for o in output.split('\n') if o.strip() != '']
                except:
                    ret = to_json(output)
                if nothread:
                    return ret
                self.callback_return_pipe_exec_func(web, title, ret)
            except:
                if nothread:
                    return output
                self.callback_return_pipe_exec_func(web, title, output)
        if nothread:
            return _exec_pipe(title, opt, web.container, True, capture_stdin)
        if web.pipe_th is not None:
            web.pipe_th.raise_exception()
        self.pipe_th = _web.RaiseThread(target=_exec_pipe, args=(title, opt, web.container, False, capture_stdin))
        self.pipe_th.start()
        #gevent.spawn(_exec_pipe, title, opt, self.container, False, capture_stdin)
        return dict(success='start_pipe')

