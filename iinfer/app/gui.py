from iinfer.app import app
from iinfer.app import common
from pathlib import Path
import datetime
import glob
import io
import json
import logging
import os
import re
import sys


class Web(object):
    def __init__(self, logger:logging.Logger):
        import eel
        self.logger = logger
        eel.init("iinfer/web")

    def start(self, width:int=1080, height:int=600, web_host:str="localhost", web_port:int=8080):
        import eel
        self.logger.info(f"Start eel web on http://{web_host}:{web_port}")
        eel.js_init({})

        @eel.expose
        def get_mode_opt():
            return ['', 'client', 'postprocess', 'server', 'redis', 'install']

        @eel.expose
        def get_cmd_opt(mode):
            if mode == "client":
                return ['', 'deploy', 'start', 'stop', 'predict', 'deploy_list', 'undeploy', 'predict_type_list', 'capture']
            elif mode == "server":
                return ['', 'start', 'stop']
            elif mode == "postprocess":
                return ['', 'det_filter', 'det_jadge', 'cls_jadge', 'csv', 'httpreq']
            elif mode == "redis":
                return ['', 'docker_run', 'docker_stop']
            elif mode == "install":
                return ['', 'redis', 'server', 'onnx', 'mmdet', 'mmcls', 'mmpretrain']
            else:
                return ['Please select mode.']

        @eel.expose
        def get_opt_opt(mode, cmd):
            if mode == "client":
                if cmd == "deploy":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="model_file", type="file", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="model_conf_file", type="file", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="model_img_width", type="int", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="model_img_height ", type="int", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="predict_type", type="str", default="", required=False, multi=False, hide=False, choise=[key for key in common.BASE_MODELS.keys()]),
                        dict(opt="custom_predict_py", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="label_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="color_file", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="overwrite", type="bool", default=True, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "deploy_list":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "undeploy":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "start":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="model_provider", type="str", default="CPUExecutionProvider", required=False, multi=False, hide=True,
                             choise=['CPUExecutionProvider', 'CUDAExecutionProvider', 'TensorrtExecutionProvider']),
                        dict(opt="use_track", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="gpuid", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "predict_type_list":
                    return []
                elif cmd == "stop":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "predict":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="image_type", type="str", default="jpeg", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                        dict(opt="output_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "capture":
                    return [
                        dict(opt="capture_device", type="str", default="0", required=True, multi=False, hide=True, choise=None),
                        dict(opt="image_type", type="str", default="capture", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                        dict(opt="capture_frame_width", type="int", default=640, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_frame_height", type="int", default=480, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_fps", type="int", default=5, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_count", type="int", default=5, required=False, multi=False, hide=False, choise=None),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False])
                    ]
                return []
            elif mode == "server":
                if cmd == "start":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="data", type="file", default=str(Path(common.HOME_DIR) / ".iinfer"), required=False, multi=False, hide=False, choise=None)
                    ]
                elif cmd == "stop":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None)
                    ]
                return []
            elif mode == "postprocess":
                if cmd == "det_filter":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="score_th", type="float", default="0.0", required=False, multi=False, hide=False, choise=None),
                        dict(opt="width_th", type="int", default="0", required=False, multi=False, hide=False, choise=None),
                        dict(opt="height_th", type="int", default="0", required=False, multi=False, hide=False, choise=None),
                        dict(opt="classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False])
                    ]
                elif cmd == "det_jadge":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ok_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ng_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ext_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False])
                    ]
                elif cmd == "cls_jadge":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ok_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ng_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_score_th", type="float", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ext_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False])
                    ]
                elif cmd == "csv":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="out_headers", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="noheader", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False])
                    ]
                elif cmd == "httpreq":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="json_connectstr", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="img_connectstr", type="str", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="fileup_name", type="str", default="file", required=True, multi=False, hide=False, choise=None)
                    ]
                return []
            elif mode == "redis":
                if cmd == "docker_run":
                    return [
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                    ]
                elif cmd == "docker_stop":
                    return [
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None)
                    ]
                return []
            elif mode == "install":
                if cmd == "onnx":
                    return []
                elif cmd == "mmdet":
                    return []
                elif cmd == "redis":
                    return [
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None)
                    ]
                elif cmd == "server":
                    return [
                        dict(opt="data", type="file", default=str(Path(common.HOME_DIR) / ".iinfer"), required=False, multi=False, hide=False, choise=None)
                    ]
                return []
            return ['-']

        @eel.expose
        def get_opt():
            return {
                "width": width,
                "height": height,
                "web_host": web_host,
                "web_port": web_port
            }

        @eel.expose
        def list_cmd():
            paths = glob.glob(str(common.HOME_DIR / ".iinfer" / "cmd-*.json"))
            return [common.loadopt(path) for path in paths]

        @eel.expose
        def save_cmd(title, opt):
            opt_path = common.HOME_DIR / ".iinfer" / f"cmd-{title}.json"
            self.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
            common.saveopt(opt, opt_path)

        @eel.expose
        def load_cmd(title):
            opt_path = common.HOME_DIR / ".iinfer" / f"cmd-{title}.json"
            return common.loadopt(opt_path)

        @eel.expose
        def del_cmd(title):
            opt_path = common.HOME_DIR / ".iinfer" / f"cmd-{title}.json"
            self.logger.info(f"del_cmd: opt_path={opt_path}")
            opt_path.unlink()

        @eel.expose
        def exec_cmd(title, opt):
            self.logger.info(f"exec_cmd: title={title}, opt={opt}")
            opt_schema = get_opt_opt(opt['mode'], opt['cmd'])
            opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
            for key, val in opt.items():
                schema = [schema for schema in opt_schema if schema['opt'] == key]
                if len(schema) == 0 or val == '':
                    continue
                if schema[0]['type'] == 'bool':
                    if val:
                        opt_list.append(f"--{key}")
                    continue
                else:
                    opt_list.append(f"--{key}")
                if type(val) == list:
                    opt_list += val
                else:
                    opt_list.append(val)
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            app.main(opt_list)
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            try:
                return json.loads(output)
            except:
                return output
            """
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            def main_call(opt_list):
                app.main(opt_list)
                print('\n')
            th = threading.Thread(target=main_call, args=(opt_list, ))
            th.start()

            while th.is_alive():
                line = captured_output.readline()
                line = line.strip()
                if line == '':
                    continue
                try:
                    yield json.loads(line)
                except:
                    yield line
            sys.stdout = old_stdout
            """
        @eel.expose
        def list_tree(current_path):
            #if current_path is None or current_path == '':
            #    drive_list = [Path(f'{d}:') for d in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if os.path.exists(f'{d}:')]

            current_path = Path.cwd() if current_path is None or current_path=='' else Path(current_path)
            current_path = current_path if current_path.is_dir() else current_path.parent
            path_tree = {}
            def mk_key(path):
                return re.sub('[\s:\\\\/,\.#$%^&!@*\(\)\{\}\[\]\'\"\`]', '_',str(path))
            def ts2str(ts):
                return datetime.datetime.fromtimestamp(ts)
            for i, part in enumerate(current_path.parts):
                path = Path('/'.join(current_path.parts[:i+1]))
                if not os.access(path, os.R_OK):
                    continue
                path_key = mk_key(path)
                children = None
                if path.is_dir():
                    children = {mk_key(p):dict(name=p.name, is_dir=p.is_dir(), path=str(p), size=p.stat().st_size, last=ts2str(p.stat().st_mtime)) for p in path.iterdir()}
                path_tree[path_key] = dict(name=part, is_dir=path.is_dir(), path=str(path), children=children, size=path.stat().st_size, last=ts2str(path.stat().st_mtime))
            return path_tree

        eel.start("main.html", size=(width, height), block=True, port=web_port, host=web_host, close_callback=self.stop)

    def stop(self, route, websockets):
        self.logger.info(f"Stop eel web. {route}")
        #exit(0)

