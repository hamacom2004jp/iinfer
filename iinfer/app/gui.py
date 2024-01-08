from iinfer import version
from iinfer.app import app
from iinfer.app import common
from pathlib import Path
import datetime
import glob
import iinfer
import io
import json
import logging
import os
import re
import sys
import threading
import traceback


class Web(object):
    def __init__(self, logger:logging.Logger, data:Path):
        import eel
        eel.init(str(Path(iinfer.__file__).parent / "web"))
        self.logger = logger
        self.data = data
        common.mkdirs(self.data)

    def start(self, width:int=1080, height:int=700, web_host:str="localhost", web_port:int=8080):
        import eel
        self.logger.info(f"Start eel web on http://{web_host}:{web_port}")

        @eel.expose
        def get_mode_opt():
            return ['', 'client', 'postprocess', 'server', 'redis', 'install']

        @eel.expose
        def get_cmd_opt(mode):
            if mode == "client":
                return ['', 'deploy', 'start', 'stop', 'predict', 'deploy_list', 'undeploy', 'predict_type_list', 'capture']
            elif mode == "server":
                return ['', 'start', 'stop', 'list']
            elif mode == "postprocess":
                return ['', 'det_filter', 'det_jadge', 'cls_jadge', 'csv', 'httpreq']
            elif mode == "redis":
                return ['', 'docker_run', 'docker_stop']
            elif mode == "install":
                return ['', 'redis', 'server', 'onnx', 'mmdet', 'mmcls', 'mmpretrain', 'mmrotate']
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
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
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
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "deploy_list":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "undeploy":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "start":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="model_provider", type="str", default="CPUExecutionProvider", required=False, multi=False, hide=True,
                             choise=['CPUExecutionProvider', 'CUDAExecutionProvider', 'TensorrtExecutionProvider']),
                        dict(opt="use_track", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="gpuid", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="60", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "predict_type_list":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "stop":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "predict":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="image_type", type="str", default="jpeg", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                        dict(opt="output_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "capture":
                    return [
                        dict(opt="capture_device", type="str", default="0", required=True, multi=False, hide=True, choise=None),
                        dict(opt="image_type", type="str", default="capture", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                        dict(opt="capture_frame_width", type="int", default=640, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_frame_height", type="int", default=480, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_fps", type="int", default=5, required=False, multi=False, hide=True, choise=None),
                        dict(opt="capture_count", type="int", default=5, required=False, multi=False, hide=False, choise=None),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                return []
            elif mode == "server":
                if cmd == "start":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="data", type="file", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "stop":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "list":
                    return [
                        dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "det_jadge":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ok_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ok_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ng_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ext_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "cls_jadge":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="ok_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ok_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ok_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ng_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ng_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_score_th", type="float", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="ext_classes", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="ext_labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                        dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "csv":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="out_headers", type="str", default=False, required=False, multi=True, hide=False, choise=None),
                        dict(opt="noheader", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "httpreq":
                    return [
                        dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                        dict(opt="json_connectstr", type="str", default="", required=True, multi=False, hide=False, choise=None),
                        dict(opt="img_connectstr", type="str", default="", required=False, multi=False, hide=False, choise=None),
                        dict(opt="fileup_name", type="str", default="file", required=True, multi=False, hide=False, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                return []
            elif mode == "redis":
                if cmd == "docker_run":
                    return [
                        dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                        dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "docker_stop":
                    return [
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                return []
            elif mode == "install":
                if cmd == "onnx":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "mmdet":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "mmcls":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "mmpretrain":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "mmrotate":
                    return [
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "redis":
                    return [
                        dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                    ]
                elif cmd == "server":
                    return [
                        dict(opt="data", type="file", default=None, required=False, multi=False, hide=False, choise=None),
                        dict(opt="install_iinfer", type="str", default='iinfer', required=False, multi=False, hide=True, choise=None),
                        dict(opt="install_onnx", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                        dict(opt="install_mmdet", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                        dict(opt="install_mmcls", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                        dict(opt="install_mmpretrain", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                        dict(opt="install_mmrotate", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                        dict(opt="stdout_save", type="file", default="", required=False, multi=False, hide=True, choise=None),
                        dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
            paths = glob.glob(str(self.data / "cmd-*.json"))
            ret = [common.loadopt(path) for path in paths]
            return ret

        @eel.expose
        def save_cmd(title, opt):
            opt_path = self.data / f"cmd-{title}.json"
            self.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
            common.saveopt(opt, opt_path)

        @eel.expose
        def load_cmd(title):
            opt_path = self.data / f"cmd-{title}.json"
            return common.loadopt(opt_path)

        @eel.expose
        def del_cmd(title):
            opt_path = self.data / f"cmd-{title}.json"
            self.logger.info(f"del_cmd: opt_path={opt_path}")
            opt_path.unlink()

        def mk_opt_list(opt):
            opt_schema = get_opt_opt(opt['mode'], opt['cmd'])
            opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
            for key, val in opt.items():
                if key in ['stdout_save', 'stdout_log']:
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
                        opt_list.append(str(v))
                elif val is not None and val != '':
                    opt_list.append(f"--{key}")
                    opt_list.append(str(val))
            return opt_list
            
        @eel.expose
        def exec_cmd(title, opt):
            self.logger.info(f"exec_cmd: title={title}, opt={opt}")
            opt_list = mk_opt_list(opt)
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            try:
                app.main(opt_list)
                output = captured_output.getvalue()
            except Exception as e:
                output = list(traceback.TracebackException.from_exception(e).format())
            sys.stdout = old_stdout
            if 'stdout_save' in opt and opt['stdout_save'] != '':
                with open(opt['stdout_save'], ('a' if type(output)==str else 'wb')) as f:
                    f.write(output)
            if 'stdout_log' in opt and opt['stdout_log']:
                eel.js_console_modal_log_func(output)
            try:
                return json.loads(output)
            except:
                return output
            """
            captured_output = io.StringIO()
            def main_call(opt_list, captured_output):
                old_stdout = sys.stdout
                sys.stdout = captured_output
                app.main(opt_list)
                sys.stdout = old_stdout
            th = threading.Thread(target=main_call, args=(opt_list, captured_output))
            th.start()

            output = ''
            while th.is_alive():
                line = captured_output.getvalue()
                if line.strip() == '':
                    continue
                output += line
                eel.js_console_modal_log_func(line)
            try:
                return json.loads(output)
            except:
                return output
            """

        @eel.expose
        def raw_cmd(title, opt):
            self.logger.info(f"raw_cmd: title={title}, opt={opt}")
            opt_list = mk_opt_list(opt)
            return [dict(type='cmdline',raw=' '.join(['iinfer']+opt_list)),
                    dict(type='optjson',raw=json.dumps(opt))]

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

        @eel.expose
        def list_pipe():
            paths = glob.glob(str(self.data / "pipe-*.json"))
            return [common.loadopt(path) for path in paths]

        @eel.expose
        def exec_pipe(title, opt):
            self.logger.info(f"exec_pipe: title={title}, opt={opt}")
            pipe_outputs = []
            for i, cmd_title in enumerate(opt['pipe_cmd']):
                cmd_opt = load_cmd(cmd_title)
                cmd_output = exec_cmd(cmd_title, cmd_opt)
                pipe_outputs.append(dict(no=i, title=cmd_title, output=cmd_output))
            return pipe_outputs

        @eel.expose
        def raw_pipe(title, opt):
            self.logger.info(f"raw_pipe: title={title}, opt={opt}")
            pipe_outputs = []
            for i, cmd_title in enumerate(opt['pipe_cmd']):
                cmd_opt = load_cmd(cmd_title)
                cmd_output = raw_cmd(cmd_title, cmd_opt)
                cmdline = cmd_output[0]['raw']
                optjson = cmd_output[1]['raw']
                pipe_outputs.append(dict(no=i, title=cmd_title, cmdline=cmdline, optjson=optjson))
            return pipe_outputs

        @eel.expose
        def save_pipe(title, opt):
            opt_path = self.data / f"pipe-{title}.json"
            self.logger.info(f"save_pipe: opt_path={opt_path}, opt={opt}")
            common.saveopt(opt, opt_path)

        @eel.expose
        def del_pipe(title):
            opt_path = self.data / f"pipe-{title}.json"
            self.logger.info(f"del_pipe: opt_path={opt_path}")
            opt_path.unlink()

        @eel.expose
        def load_pipe(title):
            opt_path = self.data / f"pipe-{title}.json"
            return common.loadopt(opt_path)

        @eel.expose
        def copyright():
            return version.__copyright__

        @eel.expose
        def versions_iinfer():
            return version.__description__.split('\n')

        @eel.expose
        def versions_used():
            with open(Path(iinfer.__file__).parent / 'licenses' / 'files.txt', 'r', encoding='utf-8') as f:
                ret = []
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            return ret

        eel.js_console_modal_log_func('== console log start ==\n')
        eel.start("main.html", size=(width, height), block=True, port=web_port, host=web_host, close_callback=self.stop)

    def stop(self, route, websockets):
        self.logger.info(f"Stop eel web. {route}")
        exit(0)

