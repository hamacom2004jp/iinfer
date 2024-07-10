from iinfer import version
from iinfer.app import app, common, options
from iinfer.app.commons import convert, redis_client
from pathlib import Path
from typing import List
import webbrowser
import bottle
import bottle_websocket
import cv2
import datetime
import glob
import gevent
import html
import iinfer
import io
import json
import logging
import os
import re
import queue
import signal
import subprocess
import sys
import threading
import traceback
import tempfile
import time

class Web(options.Options):
    def __init__(self, logger:logging.Logger, data:Path, redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server',
                 client_only:bool=False, filer_html:str=None, showimg_html:str=None, assets:List[str]=None, gui_mode:bool=False):
        """
        iinferクライアント側のwebapiサービス

        Args:
            logger (logging): ロガー
            data (Path): コマンドやパイプラインの設定ファイルを保存するディレクトリ
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): 推論サーバーのサービス名. Defaults to 'server'.
            client_only (bool, optional): クライアントのみのサービスかどうか. Defaults to False.
            filer_html (str, optional): ファイラーのHTMLファイル. Defaults to None.
            showimg_html (str, optional): 画像表示のHTMLファイル. Defaults to None.
            assets (List[str], optional): 静的ファイルのリスト. Defaults to None.
            gui_mode (bool, optional): GUIモードかどうか. Defaults to False.
        """
        super().__init__()
        self.logger = logger
        self.data = data
        self.container = dict()
        self.output_size_th = 1024*1024*5
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = svname
        self.client_only = client_only
        if self.client_only:
            self.svname = 'client'
        self.filer_html = Path(filer_html) if filer_html is not None else None
        self.showimg_html = Path(showimg_html) if showimg_html is not None else None
        self.assets = [Path(a) for a in assets] if assets is not None else None
        self.filer_html_data = None
        self.showimg_html_data = None
        self.assets_data = None
        self.gui_mode = gui_mode
        common.mkdirs(self.data)
        self.img_queue = queue.Queue(1000)
        self.cb_queue = queue.Queue(1000)

    def mk_curl_fileup(self, cmd_opt):
        if 'mode' not in cmd_opt or 'cmd' not in cmd_opt:
            return ""
        curl_fileup = set()
        for ref in self.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd']):
            if 'fileio' not in ref or ref['fileio'] != 'in':
                continue
            if ref['opt'] in cmd_opt and cmd_opt[ref['opt']] != '':
                curl_fileup.add(f'-F "{ref["opt"]}=@&lt;{ref["opt"]}&gt;"')
        if 'stdin' in cmd_opt and cmd_opt['stdin']:
            curl_fileup.add(f'-F "input_file=@&lt;input_file&gt;"')
        return " ".join(curl_fileup)

    def list_cmd(self, kwd):
        if kwd is None or kwd == '':
            kwd = '*'
        paths = glob.glob(str(self.data / f"cmd-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        return ret

    def save_cmd(self, title, opt):
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = self.data / f"cmd-{title}.json"
        self.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)
        return dict(success=f'Command "{title}" saved in "{opt_path}".')

    def load_cmd(self, title):
        opt_path = self.data / f"cmd-{title}.json"
        return common.loadopt(opt_path)

    def del_cmd(self, title):
        opt_path = self.data / f"cmd-{title}.json"
        self.logger.info(f"del_cmd: opt_path={opt_path}")
        opt_path.unlink()

    def mk_opt_list(self, opt:dict):
        opt_schema = self.get_cmd_choices(opt['mode'], opt['cmd'])
        opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
        file_dict = dict()
        for key, val in opt.items():
            if key in ['stdout_log', 'capture_stdout']:
                continue
            schema = [schema for schema in opt_schema if schema['opt'] == key]
            if len(schema) == 0 or val == '':
                continue
            if schema[0]['type'] == 'bool':
                if val:
                    opt_list.append(f"--{key}")
                continue
            if type(val) == list:
                for v in val:
                    if v is None or v == '':
                        continue
                    opt_list.append(f"--{key}")
                    if str(v).find(' ') >= 0:
                        opt_list.append(f'"{v}"')
                    else:
                        opt_list.append(str(v))
            elif val is not None and val != '':
                opt_list.append(f"--{key}")
                if str(val).find(' ') >= 0:
                    opt_list.append(f'"{val}"')
                else:
                    opt_list.append(str(val))
            if 'fileio' in schema and schema[0]['fileio'] == 'in' and type(val) != str:
                file_dict[key] = val
        return opt_list, file_dict

    def bbforce_cmd(self):
        self.logger.info(f"bbforce_cmd")
        try:
            self.container['iinfer_app'].sv.is_running = False
        except Exception as e:
            pass
        try:
            self.container['iinfer_app'].cl.is_running = False
        except Exception as e:
            pass
        try:
            self.container['iinfer_app'].web.is_running = False
        except Exception as e:
            pass
        try:
        #    self.container['pipe_proc'].send_signal(signal.CTRL_C_EVENT)
            self.container['pipe_proc'].terminate()
        except Exception as e:
            pass

    def chk_client_only(self, opt):
        if not self.client_only:
            return False, None
        use_redis = self.get_cmd_attr(opt['mode'], opt['cmd'], "use_redis")
        if use_redis == self.USE_REDIS_FALSE:
            return False, None
        output = dict(warn=f'Commands that require a connection to the iinfer server are not available.'
                        +f' (mode={opt["mode"]}, cmd={opt["cmd"]}) '
                        +f'The cause is that the client_only option is specified when starting web mode.')
        if use_redis == self.USE_REDIS_TRUE:
            return True, output
        for c in self.get_cmd_attr(opt['mode'], opt['cmd'], "choise"):
            if c['opt'] == 'local_data' and 'local_data' in opt and opt['local_data'] is None:
                return True, output
        return False, None

    def exec_cmd(self, title, opt, nothread=False):
        self.container['iinfer_app'] = app.IinferApp()
        def _exec_cmd(iinfer_app:app.IinferApp, title, opt, nothread=False):
            self.logger.info(f"exec_cmd: title={title}, opt={opt}")
            ret, output = self.chk_client_only(opt)
            if ret:
                if nothread: return output
                self.callback_return_pipe_exec_func(title, output)
                return

            opt_list, file_dict = self.mk_opt_list(opt)
            old_stdout = sys.stdout

            if 'capture_stdout' in opt and opt['capture_stdout'] and 'stdin' in opt and opt['stdin']:
                output = dict(warn=f'The "stdin" and "capture_stdout" options cannot be enabled at the same time. This is because it may cause a memory squeeze.')
                if nothread: return output
                self.callback_return_pipe_exec_func(title, output)
                return
            if 'capture_stdout' in opt and opt['capture_stdout']:
                sys.stdout = captured_output = io.StringIO()
            try:
                iinfer_app.main(args_list=opt_list, file_dict=file_dict)
                self.logger.disabled = False # ログ出力を有効にする
                if 'capture_stdout' in opt and opt['capture_stdout']:
                    output = captured_output.getvalue().strip()
                    output_size = len(output)
                    if output_size > self.output_size_th:
                        o = output.split('\n')
                        if len(o) > 0:
                            osize = len(o[0])
                            oidx = int(self.output_size_th / osize)
                            if oidx > 0:
                                output = '\n'.join(o[-oidx:])
                            else:
                                output = [dict(warn=f'The captured stdout was discarded because its size was larger than {self.output_size_th} bytes.')]
                        else:
                            output = [dict(warn=f'The captured stdout was discarded because its size was larger than {self.output_size_th} bytes.')]
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                self.logger.disabled = False # ログ出力を有効にする
                self.logger.info(f'exec_cmd error. {traceback.format_exc()}')
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            sys.stdout = old_stdout
            if 'stdout_log' in opt and opt['stdout_log']:
                self.callback_console_modal_log_func(output)
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
                self.callback_return_cmd_exec_func(title, ret)
            except:
                self.logger.warning(f'exec_cmd error.', exec_info=True)
                if nothread:
                    return output
                self.callback_return_cmd_exec_func(title, output)
        if nothread:
            return _exec_cmd(self.container['iinfer_app'], title, opt, True)
        th = threading.Thread(target=_exec_cmd, args=(self.container['iinfer_app'], title, opt, False))
        th.start()
        return [dict(warn='start_cmd')]

    def raw_cmd(self, title:str, opt:dict):
        self.logger.info(f"raw_cmd: title={title}, opt={opt}")
        opt_list, _ = self.mk_opt_list(opt)
        if 'stdout_log' in opt: del opt['stdout_log']
        if 'capture_stdout' in opt: del opt['capture_stdout']
        curl_cmd_file = self.mk_curl_fileup(opt)
        return [dict(type='cmdline',raw=' '.join(['python','-m','iinfer']+opt_list)),
                dict(type='optjson',raw=json.dumps(opt, default=common.default_json_enc)),
                dict(type='curlcmd',raw=f'curl {curl_cmd_file} http://localhost:8081/exec_cmd/{title}')]

    def list_tree(self, current_path):
        current_path = Path.cwd() if current_path is None or current_path=='' else Path(current_path)
        current_path = current_path if current_path.is_dir() else current_path.parent
        path_tree = {}
        def mk_key(path):
            return re.sub(r'[\s:\\\\/,\.#$%^&!@*\(\)\{\}\[\]\'\"\`]', '_',str(path))
        def ts2str(ts):
            return datetime.datetime.fromtimestamp(ts)
        for i, part in enumerate(current_path.parts):
            path = Path('/'.join(current_path.parts[:i+1]).replace('//', '/'))
            if not os.access(path, os.R_OK):
                continue
            path_key = mk_key(path)
            children = None
            if path.is_dir():
                try:
                    children = {mk_key(p):dict(name=p.name, is_dir=p.is_dir(), path=str(p), size=p.stat().st_size, last=ts2str(p.stat().st_mtime)) for p in path.iterdir()}
                except:
                    children = {}
            path_tree[path_key] = dict(name=part, is_dir=path.is_dir(), path=str(path), children=children, size=path.stat().st_size, last=ts2str(path.stat().st_mtime))
        return path_tree
    
    def list_downloads(self, current_path, root_path=None):
        if type(current_path) == str:
            current_path = current_path[1:] if current_path.startswith('/') else current_path
            current_path = self.data if current_path is None or current_path=='' else self.data / current_path
            root_path = current_path
        if current_path.is_file():
            svpath = str(current_path).replace(str(self.data), '')
            rpath = str(current_path).replace(str(root_path), '')[1:]
            rpath = str(Path(root_path.name) / rpath)
            #dlpath = cpath.replace(str(Path(rpath).parent), '')
            return [dict(svpath=svpath, rpath=rpath)]
        download_files = []
        if current_path.is_dir():
            for f in current_path.iterdir():
                download_files = download_files + self.list_downloads(f, root_path)
        return download_files

    def load_result(self, current_path):
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

    def load_capture(self, current_path):
        current_path = Path(current_path)
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
    
    def list_pipe(self, kwd):
        if kwd is None or kwd == '':
            kwd = '*'
        paths = glob.glob(str(self.data / f"pipe-{kwd}.json"))
        return [common.loadopt(path) for path in paths]

    def exec_pipe(self, title, opt, nothread=False):
        self.logger.info(f"exec_pipe: title={title}, opt={opt}")
        def to_json(o):
            res_json = json.loads(o)
            if 'output_image' in res_json and 'output_image_shape' in res_json:
                img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                img_bytes = convert.npy2imgfile(img_npy, image_type='png')
                res_json["output_image"] = convert.bytes2b64str(img_bytes)
            return res_json
        def _exec_pipe(title, opt, container, nothread=False):
            capture_stdout = True
            for i, cmd_title in enumerate(opt['pipe_cmd']):
                if cmd_title == '':
                    continue
                cmd_opt = self.load_cmd(cmd_title)
                #cmd_ref = self.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd'])
                #chk_stdin = len([ref for ref in cmd_ref if ref['opt'] == 'stdin']) > 0
                #chk_input_file = len([ref for ref in cmd_ref if ref['opt'] == 'input_file']) > 0
                if 'capture_stdout' in cmd_opt:
                    capture_stdout = cmd_opt['capture_stdout']
                else:
                    capture_stdout = True
                if 'output_csv' in cmd_opt and cmd_opt['output_csv'] != '':
                    output = dict(warn=f'The "output_csv" option is not supported in pipe. ({cmd_title})')
                    self.callback_return_pipe_exec_func(title, output)
                    return
            cmdline = None
            has_warn = False
            for cl in self.raw_pipe(title, opt):
                if cl['type'] == 'cmdline':
                    cmdline = cl['raw']
                if cl['type'] == 'warn':
                    self.callback_return_pipe_exec_func(title, cl)
                    has_warn = True
            if cmdline is None:
                self.callback_return_pipe_exec_func(title, dict(warn='No command to execute.'))
                has_warn = True
            if has_warn: return
            try:
                container['pipe_proc'] = subprocess.Popen(cmdline, shell=True, text=True, encoding='utf-8',
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
                            if len(o) < self.output_size_th:
                                try:
                                    o = to_json(o)
                                except:
                                    pass
                                self.callback_return_stream_log_func(o)
                            else:
                                o = [dict(warn=f'The captured stdout was discarded because its size was larger than {self.output_size_th} bytes.')]
                                self.callback_return_stream_log_func(o)
                        except:
                            o = [dict(warn=f'<pre>{html.escape(o)}</pre><br><pre>{html.escape(traceback.format_exc())}</pre>')]
                            self.callback_return_stream_log_func(o)
                if capture_stdout:
                    container['pipe_proc'].stdout.read() # 最後のストリームは読み捨て
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            if 'stdout_log' in opt and cmd_opt['stdout_log']:
                self.callback_console_modal_log_func(output)
            try:
                try:
                    ret = [to_json(o) for o in output.split('\n') if o.strip() != '']
                except:
                    ret = to_json(output)
                if nothread:
                    return ret
                self.callback_return_pipe_exec_func(title, ret)
            except:
                if nothread:
                    return output
                self.callback_return_pipe_exec_func(title, output)
        if nothread:
            return _exec_pipe(title, opt, self.container, True)
        gevent.spawn(_exec_pipe, title, opt, self.container)
        return dict(success='start_pipe')

    def raw_pipe(self, title, opt):
        self.logger.info(f"raw_pipe: title={title}, opt={opt}")
        cmdlines = []
        errormsg = []
        curl_cmd_file = ""
        for i, cmd_title in enumerate(opt['pipe_cmd']):
            if cmd_title == '':
                continue
            cmd_opt = self.load_cmd(cmd_title)
            cmd_ref = self.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd'])
            chk_stdin = len([ref for ref in cmd_ref if ref['opt'] == 'stdin']) > 0

            if 'output_csv' in cmd_opt and cmd_opt['output_csv'] != '':
                errormsg.append(f'The "output_csv" option is not supported in pipe. ({cmd_title})')
            if i>0:
                if chk_stdin and ('stdin' not in cmd_opt or not cmd_opt['stdin']):
                    errormsg.append(f'The "stdin" option should be specified for the second and subsequent commands. ({cmd_title})')
                if chk_stdin and 'pred_input_type' in cmd_opt and cmd_opt['pred_input_type'] not in ['capture', 'prompt']:
                    errormsg.append(f'When using the "stdin" option, "pred_input_type" cannot be other than "capture" or "prompt". ({cmd_title})')
                for ref in cmd_ref:
                    if 'fileio' in ref and ref['fileio'] == 'in' and ref['opt'] in cmd_opt and cmd_opt[ref['opt']] != '' and len([v for v in cmd_opt[ref['opt']] if v != '']) > 0:
                        errormsg.append(f'The "{ref["opt"]}" option should not be specified in a second or subsequent command. ({cmd_title})')
            if i==0:
                if 'request_files' in opt and len(opt['request_files']) > 0:
                    for fn in opt['request_files']:
                        if fn in cmd_opt:
                            cmd_opt[fn] = opt['request_files'][fn]
                curl_cmd_file = self.mk_curl_fileup(cmd_opt)

            cmd_output = self.raw_cmd(cmd_title, cmd_opt)
            cmdlines.append(cmd_output[0]["raw"])

        curl_opt = json.dumps(opt, default=common.default_json_enc)
        curl_opt = curl_opt.replace('"', '\\"')
        ret = [dict(type='cmdline', raw=' | '.join(cmdlines)),
                dict(type='curlcmd', raw=f'curl {curl_cmd_file} http://localhost:8081/exec_pipe/{title}')]
        ret += [dict(type='warn', raw=em) for em in errormsg]
        return ret

    def save_pipe(self, title, opt):
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = self.data / f"pipe-{title}.json"
        self.logger.info(f"save_pipe: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)
        return dict(success=f'Pipeline "{title}" saved in "{opt_path}".')

    def del_pipe(self, title):
        opt_path = self.data / f"pipe-{title}.json"
        self.logger.info(f"del_pipe: opt_path={opt_path}")
        opt_path.unlink()

    def load_pipe(self, title):
        opt_path = self.data / f"pipe-{title}.json"
        return common.loadopt(opt_path)

    def copyright(self):
        return version.__copyright__

    def versions_iinfer(self):
        logo = [version.__logo__]
        return logo + version.__description__.split('\n')

    def versions_used(self):
        with open(Path(iinfer.__file__).parent / 'licenses' / 'files.txt', 'r', encoding='utf-8') as f:
            ret = []
            for i, line in enumerate(f.readlines()):
                parts = line.strip().split('\t')
                ret.append(parts)
        return ret
    
    def filer_upload(self, request:bottle.Request):
        q = request.query
        svpath = q['svpath']
        opt = dict(mode='client', cmd='file_upload',
                   host=q['host'], port=q['port'], password=q['password'], svname=q['svname'],
                   local_data=q['local_data'])
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
                ret = self.exec_cmd("file_upload", opt, nothread=True)
                if len(ret) == 0 or 'success' not in ret[0]:
                    return str(ret)
        return 'upload success'
        #return f'upload {upload.filename}'

    def callback_console_modal_log_func(self, output:dict):
        self.cb_queue.put(('js_console_modal_log_func', None, output))
    
    def callback_return_cmd_exec_func(self, title, output:dict):
        self.cb_queue.put(('js_return_cmd_exec_func', title, output))

    def callback_return_pipe_exec_func(self, title, output):
        self.cb_queue.put(('js_return_pipe_exec_func', title, output))

    def callback_return_stream_log_func(self, output):
        self.cb_queue.put(('js_return_stream_log_func', None, output))

    def gui_callback(self):
        wsock = bottle.request.environ.get('wsgi.websocket') # type: ignore
        if not wsock:
            bottle.abort(400, 'Expected WebSocket request.')
        while True:
            outputs = None
            try:
                cmd, title, output = self.cb_queue.get(block=True, timeout=0.001)
                outputs = dict(cmd=cmd, title=title, output=output)
                wsock.send(json.dumps(outputs, default=common.default_json_enc))
            except queue.Empty:
                gevent.sleep(0.001)
            except:
                self.logger.warning('websocket error', exc_info=True)
                gevent.sleep(10)

    def to_str(self, o):
        if type(o) == dict:
            return json.dumps(o, default=common.default_json_enc)
        elif type(o) == list and len(o) > 0 and type(o[0]) == dict:
            return json.dumps(o, default=common.default_json_enc)
        return str(o)

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081):
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.logger.info(f"Start web. allow_host={self.allow_host} listen_port={self.listen_port}")

        app = bottle.Bottle()
        bottle.debug(True)

        if self.filer_html is not None:
            if not self.filer_html.is_file():
                raise FileNotFoundError(f'filer_html is not found. ({self.filer_html})')
            with open(self.filer_html, 'r', encoding='utf-8') as f:
                self.filer_html_data = f.read()
        if self.showimg_html is not None:
            if not self.showimg_html.is_file():
                raise FileNotFoundError(f'showimg_html is not found. ({self.showimg_html})')
            with open(self.showimg_html, 'r', encoding='utf-8') as f:
                self.showimg_html_data = f.read()
        if self.assets is not None:
            if type(self.assets) != list:
                raise TypeError(f'assets is not list. ({self.assets})')
            for i, asset in enumerate(self.assets):
                if not asset.is_file():
                    raise FileNotFoundError(f'asset is not found. ({asset})')
                with open(asset, 'r', encoding='utf-8') as f:
                    asset_data = f.read()
                    def asset_func(asset_data):
                        @app.route(f'/{asset.name}')
                        def func():
                            return asset_data
                        return func
                    asset_func(asset_data)

        redis_cli = None
        if not self.client_only:
            redis_cli = redis_client.RedisClient(self.logger, host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname)

        @app.route('/bbforce_cmd')
        def bbforce_cmd():
            self.bbforce_cmd()
            return dict(success='bbforce_cmd')

        @app.route('/exec_cmd', method='POST')
        @app.route('/exec_cmd/<title>')
        @app.route('/exec_cmd/<title>', method='POST')
        def exec_cmd(title=None):
            try:
                opt = None
                if bottle.request.content_type.startswith('multipart/form-data'):
                    opt = self.load_cmd(title)
                    for fn in bottle.request.files.keys():
                        opt[fn] = bottle.request.files[fn].file
                        if fn == 'input_file': opt['stdin'] = False
                elif bottle.request.content_type.startswith('application/json'):
                    opt = bottle.request.json
                else:
                    opt = self.load_cmd(title)
                opt['capture_stdout'] = nothread = True
                opt['stdout_log'] = False
                return self.to_str(self.exec_cmd(title, opt, nothread))
            except:
                return self.to_str(dict(warn=f'Command "{title}" failed. {traceback.format_exc()}'))

        @app.route('/exec_pipe/<title>')
        @app.route('/exec_pipe/<title>', method='POST')
        def exec_pipe(title):
            upfiles = dict()
            try:
                opt = None
                if bottle.request.content_type.startswith('multipart/form-data'):
                    opt = self.load_pipe(title)
                    opt['request_files'] = dict()
                    for cmd_title in opt['pipe_cmd']:
                        if cmd_title == '':
                            continue
                        cmd_opt = self.load_cmd(cmd_title)
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
                    opt = self.load_pipe(title)
                opt['capture_stdout'] = nothread = True
                opt['stdout_log'] = False
                return self.to_str(self.exec_pipe(title, opt, nothread))
            except:
                return self.to_str(dict(warn=f'Pipeline "{title}" failed. {traceback.format_exc()}'))
            finally:
                for tfname in upfiles.values():
                    os.unlink(tfname)

        @app.route('/versions_iinfer')
        def versions_iinfer():
            return self.versions_iinfer()

        @app.route('/gui/callback')
        def gui_callback():
            return self.gui_callback()

        static_root = Path(__file__).parent.parent / 'web'

        @app.route('/')
        def index():
            return bottle.redirect('gui')
        
        @app.route('/gui')
        def gui():
            return bottle.static_file('gui.html', root=static_root)

        @app.route('/gui/list_downloads', method='POST')
        def list_downloads():
            current_path = bottle.request.forms.get('current_path')
            ret = self.list_downloads(current_path)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/list_tree', method='POST')
        def list_tree():
            current_path = bottle.request.forms.get('current_path')
            ret = self.list_tree(current_path)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/list_cmd', method='POST')
        def list_cmd():
            kwd = bottle.request.forms.get('kwd')
            ret = self.list_cmd(kwd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/get_modes')
        def get_modes():
            ret = self.get_modes()
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/get_cmds', method='POST')
        def get_cmds():
            mode = bottle.request.forms.get('mode')
            ret = self.get_cmds(mode)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/get_cmd_choices', method='POST')
        def get_cmd_choices():
            mode = bottle.request.forms.get('mode')
            cmd = bottle.request.forms.get('cmd')
            ret = self.get_cmd_choices(mode, cmd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/load_cmd', method='POST')
        def load_cmd():
            title = bottle.request.forms.get('title')
            ret = self.load_cmd(title)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/save_cmd', method='POST')
        def save_cmd():
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.save_cmd(title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/del_cmd', method='POST')
        def del_cmd():
            title = bottle.request.forms.get('title')
            self.del_cmd(title)
            bottle.response.content_type = 'application/json'
            return json.dumps({}, default=common.default_json_enc)

        @app.route('/gui/raw_cmd', method='POST')
        def raw_cmd():
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.raw_cmd(title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/list_pipe', method='POST')
        def list_pipe():
            kwd = bottle.request.forms.get('kwd')
            ret = self.list_pipe(kwd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/load_pipe', method='POST')
        def load_pipe():
            title = bottle.request.forms.get('title')
            ret = self.load_pipe(title)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/save_pipe', method='POST')
        def save_pipe():
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.save_pipe(title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/del_pipe', method='POST')
        def del_pipe():
            title = bottle.request.forms.get('title')
            self.del_pipe(title)
            bottle.response.content_type = 'application/json'
            return json.dumps({}, default=common.default_json_enc)

        @app.route('/gui/raw_pipe', method='POST')
        def raw_pipe():
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.raw_pipe(title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/load_capture', method='POST')
        def load_capture():
            current_path = bottle.request.forms.get('current_path')
            ret = self.load_capture(current_path)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/gui/load_result', method='POST')
        def load_result():
            current_path = bottle.request.forms.get('current_path')
            ret = self.load_result(current_path)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

        @app.route('/filer')
        def filer():
            if self.filer_html_data is not None:
                return self.filer_html_data
            return bottle.static_file('filer.html', root=static_root)

        @app.route('/filer/upload', method='POST')
        def filer_upload():
            return self.filer_upload(bottle.request)

        @app.route('/showimg')
        def showimg():
            if self.showimg_html_data is not None:
                return self.showimg_html_data
            return bottle.static_file('showimg.html', root=static_root)

        @app.route('/showimg/pub_img', method='POST')
        def pub_img():
            try:
                tm = time.time()
                self.logger.info(f'pub_img: start={tm}')
                if bottle.request.content_type.startswith('multipart/form-data'):
                    for fn in bottle.request.files.keys():
                        filename = bottle.request.files[fn].filename
                        self.img_queue.put((filename, bottle.request.files[fn].file.read()))
                else:
                    outputs = json.load(bottle.request.body)
                    self.img_queue.put(outputs)
                ret = self.to_str(dict(success='Added to queue.'))
                self.logger.info(f'pub_img: {time.time()-tm}')
                return ret
            except:
                self.logger.warning('pub_img error', exc_info=True)
                return self.to_str(dict(warn=f'pub_img error. {traceback.format_exc()}'))

        @app.route('/showimg/sub_img')
        def sub_img():
            wsock = bottle.request.environ.get('wsgi.websocket') # type: ignore
            if not wsock:
                bottle.abort(400, 'Expected WebSocket request.')
            while True:
                outputs = None
                try:
                    try:
                        outputs = self.img_queue.get(block=True, timeout=0.001)
                    except queue.Empty:
                        if redis_cli is not None:
                            cmd, outputs = redis_cli.recive_showimg()
                    if outputs is None:
                        gevent.sleep(0.1)
                        continue
                    if 'output_image_shape' in outputs:
                        img_npy = convert.b64str2npy(outputs["output_image"], outputs["output_image_shape"])
                        jpg = convert.img2byte(convert.npy2img(img_npy), format='jpeg')
                        jpg_url = f"data:image/jpeg;base64,{convert.bytes2b64str(jpg)}"
                        del outputs["output_image"]
                        del outputs["output_image_shape"]
                        outputs['img_url'] = jpg_url
                        outputs['img_id'] = outputs['output_image_name'].strip()
                    elif type(outputs) == tuple:
                        fn = outputs[0]
                        jpg_url = f"data:image/jpeg;base64,{convert.bytes2b64str(outputs[1])}"
                        outputs = dict(output_image_name=fn)
                        outputs['img_url'] = jpg_url
                        outputs['img_id'] = fn
                    wsock.send(json.dumps(outputs, default=common.default_json_enc))
                except Exception as e:
                    if outputs is not None:
                        self.img_queue.put(outputs) # エラーが発生した場合はキューに戻す
                        gevent.sleep(0.001)
                        continue
                    self.logger.warning('websocket error', exc_info=True)
                    gevent.sleep(10)

        @app.route('/assets/<filename:path>')
        def assets(filename):
            return bottle.static_file(filename, root=static_root / 'assets')

        @app.route('/copyright')
        def copyright():
            return self.copyright()

        @app.route('/versions_iinfer')
        def versions_iinfer():
            bottle.response.content_type = 'application/json'
            return json.dumps(self.versions_iinfer())

        @app.route('/get_server_opt')
        def get_server_opt():
            opt = dict(host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname,
                       data=str(self.data), client_only=self.client_only)
            bottle.response.content_type = 'application/json'
            return json.dumps(opt)

        @app.route('/versions_used')
        def versions_used():
            bottle.response.content_type = 'application/json'
            return json.dumps(self.versions_used())

        with open("iinfer_web.pid", mode="w", encoding="utf-8") as f:
            pid = os.getpid()
            f.write(str(pid))
            self.is_running = True
            server = _WSGIServer(host=self.allow_host, port=self.listen_port, gui_mode=self.gui_mode)
            th = threading.Thread(target=bottle.run, kwargs=dict(app=app, server=server))
            th.start()
            while self.is_running:
                gevent.sleep(1)
            server.srv.shutdown()
        Path("iinfer_web.pid").unlink(missing_ok=True)

    def stop(self):
        with open("iinfer_web.pid", mode="r", encoding="utf-8") as f:
            pid = f.read()
            os.kill(int(pid), signal.CTRL_C_EVENT)
            self.logger.info(f"Stop bottle web. allow_host={self.allow_host} listen_port={self.listen_port}")
        Path("iinfer_web.pid").unlink(missing_ok=True)

    def webcap(self, allow_host:str="0.0.0.0", listen_port:int=8082,
               image_type:str='capture', capture_frame_width:int=None, capture_frame_height:int=None,
               capture_fps:int=5, output_preview:bool=False):
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.logger.info(f"Start web. allow_host={self.allow_host} listen_port={self.listen_port}")

        app = bottle.Bottle()
        bottle.debug(True)

        @app.route('/webcap/pub_img')
        def pub_img():
            wsock = bottle.request.environ.get('wsgi.websocket') # type: ignore
            if not wsock:
                bottle.abort(400, 'Expected WebSocket request.')
            interval = float(1 / capture_fps)
            while True:
                try:
                    start = time.perf_counter()
                    cap = wsock.receive()
                    if cap is None:
                        gevent.sleep(0.001)
                        continue
                    output_image_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                    img_npy = convert.imgbytes2npy(convert.b64str2bytes(cap))
                    if capture_frame_width is not None and capture_frame_height is not None:
                        frame = cv2.resize(frame, (capture_frame_width, capture_frame_height), interpolation=cv2.INTER_NEAREST)
                    img_npy = convert.bgr2rgb(frame)
                    if output_preview:
                        # RGB画像をBGR画像に変換
                        cv2.imshow('preview', convert.bgr2rgb(img_npy))
                        cv2.waitKey(1)
                    img_b64 = None
                    if image_type == 'capture' or image_type is None:
                        image_type = 'capture'
                        img_b64 = convert.npy2b64str(img_npy)
                    else:
                        img_b64 = convert.bytes2b64str(convert.npy2imgfile(img_npy, image_type=image_type))
                    output_image_name = f"{output_image_name}.{image_type}"
                    yield image_type, img_b64, img_npy.shape[0], img_npy.shape[1], img_npy.shape[2] if len(img_npy.shape) > 2 else -1, output_image_name

                    end = time.perf_counter()
                    if interval - (end - start) > 0:
                        time.sleep(interval - (end - start))
                except Exception as e:
                    self.logger.warning('wsock error', exc_info=True)
                    break
            self.logger.info('wsock disconnected')

        server = _WSGIServer(host=self.allow_host, port=self.listen_port, gui_mode=self.gui_mode)
        bottle.run(app=app, server=server, host=allow_host, port=listen_port)

class _WSGIServer(bottle_websocket.GeventWebSocketServer):
#class _WSGIServer(bottle.WSGIRefServer):
    """
    runメソッドでWSGIRefServerを起動する際に、make_serverの戻り値をインスタンス変数にするためのクラス
    """
    def __init__(self, host='127.0.0.1', port:int=8080, gui_mode:bool=False, **options):
        super().__init__(host, port, **options)
        self.gui_mode = gui_mode

    def run(self, handler):
        import logging
        from gevent import pywsgi
        from geventwebsocket.handler import WebSocketHandler
        from geventwebsocket.logging import create_logger

        # self.srvに代入することで、shutdownを実行できるようにする
        self.srv = pywsgi.WSGIServer((self.host, self.port), handler, handler_class=WebSocketHandler)

        if not self.quiet:
            self.srv.logger = create_logger('geventwebsocket.logging')
            self.srv.logger.setLevel(logging.INFO)
            self.srv.logger.addHandler(logging.StreamHandler())

        if self.gui_mode:
            webbrowser.open(f'http://localhost:{self.port}/gui')
        self.srv.serve_forever()

    """
    def run(self, app): # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self): # Prevent reverse DNS lookups please.
                return self.client_address[0]
            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls  = self.options.get('server_class', WSGIServer)

        if ':' in self.host: # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6
        # self.srvに代入することで、shutdownを実行できるようにする
        self.srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv.serve_forever()
        self.srv.server_close()
    """