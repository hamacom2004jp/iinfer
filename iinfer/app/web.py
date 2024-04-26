from iinfer import version
from iinfer.app import app, common
from iinfer.app.commons import convert
from pathlib import Path
import bottle
import datetime
import glob
import html
import iinfer
import io
import json
import logging
import os
import re
import signal
import subprocess
import sys
import time
import threading
import traceback
import tempfile


class Web(object):
    def __init__(self, logger:logging.Logger, data:Path):
        self.logger = logger
        self.data = data
        self.container = dict()
        common.mkdirs(self.data)

    def get_mode_opt(self):
        return ['', 'client', 'postprocess', 'server', 'redis', 'install', 'web']

    def get_cmd_opt(self, mode):
        if mode == "client":
            return ['', 'deploy', 'start', 'stop', 'predict', 'deploy_list', 'undeploy', 'predict_type_list', 'capture', 'file_list', 'file_mkdir', 'file_rmdir', 'file_download', 'file_upload', 'file_remove',]
        elif mode == "server":
            return ['', 'start', 'stop', 'list']
        elif mode == "postprocess":
            return ['', 'cls_jadge', 'csv', 'det_clip', 'det_face_store', 'det_filter', 'det_jadge', 'httpreq', 'seg_bbox', 'seg_filter']
        elif mode == "redis":
            return ['', 'docker_run', 'docker_stop']
        elif mode == "install":
            return ['', 'redis', 'server', 'onnx', 'mmdet', 'mmseg', 'mmcls', 'mmpretrain']
        elif mode == "web":
            return ['', 'start', 'stop']
        else:
            return ['Please select mode.']

    def get_opt_opt(self, mode, cmd):
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
                    dict(opt="predict_type", type="str", default="", required=False, multi=False, hide=False, choise=['']+[key for key in common.BASE_MODELS.keys()]),
                    dict(opt="custom_predict_py", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="label_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="color_file", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="before_injection_type", type="str", default="", required=False, multi=True, hide=True, choise=['']+[key for key in common.BASE_BREFORE_INJECTIONS.keys()]),
                    dict(opt="before_injection_conf", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="before_injection_py", type="file", default="", required=False, multi=True, hide=True, choise=None),
                    dict(opt="after_injection_type", type="str", default="", required=False, multi=True, hide=True, choise=['']+[key for key in common.BASE_AFTER_INJECTIONS.keys()]),
                    dict(opt="after_injection_conf", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="after_injection_py", type="file", default="", required=False, multi=True, hide=True, choise=None),
                    dict(opt="overwrite", type="bool", default=True, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "deploy_list":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "undeploy":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "predict_type_list":
                return [
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "stop":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="name", type="str", default="", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
                    dict(opt="image_type", type="str", default="jpeg", required=True, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture', 'output_json']),
                    dict(opt="output_image", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_list":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_mkdir":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_rmdir":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_download":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="download_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_upload":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="upload_file", type="file", default="", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "file_remove":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
                    dict(opt="output_csv", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False])
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
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "stop":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "list":
                return [
                    dict(opt="host", type="str", default="localhost", required=True, multi=False, hide=True, choise=None),
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            return []
        elif mode == "postprocess":
            if cmd == "cls_jadge":
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
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "csv":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="out_headers", type="str", default="", required=False, multi=True, hide=False, choise=None),
                    dict(opt="noheader", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_csv", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "det_clip":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="image_type", type="str", default="capture", required=False, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                    dict(opt="clip_margin", type="int", default=0, required=False, multi=False, hide=False, choise=None),
                    dict(opt="output_csv", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "det_face_store":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="image_type", type="str", default="capture", required=False, multi=False, hide=False, choise=['bmp', 'png', 'jpeg', 'capture']),
                    dict(opt="face_threshold", type="float", default=0.0, required=False, multi=False, hide=False, choise=None),
                    dict(opt="clip_margin", type="int", default=0, required=False, multi=False, hide=False, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "det_filter":
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
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
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
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "httpreq":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="json_connectstr", type="str", default="", required=True, multi=False, hide=False, choise=None),
                    dict(opt="img_connectstr", type="str", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="fileup_name", type="str", default="file", required=True, multi=False, hide=False, choise=None),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "seg_bbox":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="del_segments", type="bool", default=True, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="nodraw_bbox", type="bool", default=True, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="nodraw_rbbox", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "seg_filter":
                return [
                    dict(opt="input_file", type="file", default="", required=False, multi=False, hide=False, choise=None),
                    dict(opt="stdin", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="logits_th", type="float", default="-100.0", required=False, multi=False, hide=False, choise=None),
                    dict(opt="classes", type="int", default="", required=False, multi=True, hide=True, choise=None),
                    dict(opt="labels", type="str", default="", required=False, multi=True, hide=False, choise=None),
                    dict(opt="nodraw", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="del_logits", type="bool", default=True, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_preview", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            return []
        elif mode == "redis":
            if cmd == "docker_run":
                return [
                    dict(opt="port", type="int", default=6379, required=True, multi=False, hide=True, choise=None),
                    dict(opt="password", type="str", default="password", required=True, multi=False, hide=True, choise=None),
                    dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "docker_stop":
                return [
                    dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            return []
        elif mode == "install":
            if cmd == "onnx":
                return [
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "mmdet":
                return [
                    dict(opt="install_use_gpu", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "mmseg":
                return [
                    dict(opt="install_use_gpu", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "mmcls":
                return [
                    dict(opt="install_use_gpu", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "mmpretrain":
                return [
                    dict(opt="install_use_gpu", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "redis":
                return [
                    dict(opt="wsl_name", type="str", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="wsl_user", type="str", default="ubuntu", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "server":
                return [
                    dict(opt="data", type="file", default=None, required=False, multi=False, hide=False, choise=None),
                    dict(opt="install_use_gpu", type="bool", default=False, required=False, multi=False, hide=False, choise=[True, False]),
                    dict(opt="install_iinfer", type="str", default='iinfer', required=False, multi=False, hide=True, choise=None),
                    dict(opt="install_onnx", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="install_mmdet", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="install_mmseg", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="install_mmcls", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="install_mmpretrain", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="output_json", type="file", default="", required=False, multi=False, hide=True, choise=None),
                    dict(opt="output_json_append", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False]),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            return []
        elif mode == "web":
            if cmd == "start":
                return [
                    dict(opt="data", type="file", default=None, required=False, multi=False, hide=False, choise=None),
                    dict(opt="allow_host", type="str", default="0.0.0.0", required=False, multi=False, hide=False, choise=None),
                    dict(opt="listen_port", type="int", default="8081", required=False, multi=False, hide=False, choise=None),
                    dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False])
                ]
            elif cmd == "stop":
                pass
            return []
        return ['-']

    def list_cmd(self, kwd):
        if kwd is None or kwd == '':
            kwd = '*'
        paths = glob.glob(str(self.data / f"cmd-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        return ret

    def save_cmd(self, title, opt):
        opt_path = self.data / f"cmd-{title}.json"
        self.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)

    def load_cmd(self, title):
        opt_path = self.data / f"cmd-{title}.json"
        return common.loadopt(opt_path)

    def del_cmd(self, title):
        opt_path = self.data / f"cmd-{title}.json"
        self.logger.info(f"del_cmd: opt_path={opt_path}")
        opt_path.unlink()

    def mk_opt_list(self, opt:dict):
        opt_schema = self.get_opt_opt(opt['mode'], opt['cmd'])
        opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
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
                    opt_list.append(str(v))
            elif val is not None and val != '':
                opt_list.append(f"--{key}")
                opt_list.append(str(val))
        return opt_list

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
            self.container['pipe_proc'].send_signal(signal.CTRL_C_EVENT)
        except Exception as e:
            pass

    def exec_cmd(self, title, opt, nothread=False):
        self.container['iinfer_app'] = app.IinferApp()
        def _exec_cmd(iinfer_app:app.IinferApp, title, opt, nothread=False):
            self.logger.info(f"exec_cmd: title={title}, opt={opt}")
            opt_list = self.mk_opt_list(opt)
            old_stdout = sys.stdout
            if 'capture_stdout' in opt and opt['capture_stdout']:
                sys.stdout = captured_output = io.StringIO()
            try:
                iinfer_app.main(opt_list)
                if 'capture_stdout' in opt and opt['capture_stdout']:
                    output = captured_output.getvalue()
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
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
                    ret = to_json(output)
                if nothread:
                    return ret
                self.callback_return_cmd_exec_func(title, ret)
            except:
                if nothread:
                    return output
                self.callback_return_cmd_exec_func(title, output)
        if nothread:
            return _exec_cmd(self.container['iinfer_app'], title, opt, True)
        th = threading.Thread(target=_exec_cmd, args=(self.container['iinfer_app'], title, opt))
        th.start()
        return [dict(warn='start_cmd')]
    
    def callback_console_modal_log_func(self, output:dict):
        raise NotImplementedError('callback_console_modal_log_func is not implemented.')
    
    def callback_return_cmd_exec_func(self, title, output:dict):
        raise NotImplementedError('callback_return_cmd_exec_func is not implemented.')

    def raw_cmd(self, title:str, opt:dict):
        self.logger.info(f"raw_cmd: title={title}, opt={opt}")
        opt_list = self.mk_opt_list(opt)
        if 'stdout_log' in opt.keys(): del opt['stdout_log']
        if 'capture_stdout' in opt.keys(): del opt['capture_stdout']
        curl_opt = json.dumps(dict(title=title, opt=opt), default=common.default_json_enc)
        curl_opt = curl_opt.replace('"', '\\"')
        return [dict(type='cmdline',raw=' '.join(['iinfer']+opt_list)),
                dict(type='optjson',raw=json.dumps(opt, default=common.default_json_enc)),
                dict(type='curlcmd',raw=f'curl -X POST -H "Content-Type: application/json" -d "{curl_opt}" http://localhost:8081/exec_cmd')]

    def list_tree(self, current_path):
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

    def load_result(self, current_path):
        current_path = Path(current_path)
        if not current_path.is_file():
            return {'warn': f'A non-file was selected.: {current_path}'}
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

    def load_capture(self, current_path):
        current_path = Path(current_path)
        if not current_path.is_file():
            return {'warn': f'A non-file was selected.: {current_path}'}
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
    
    def list_pipe(self, kwd):
        if kwd is None or kwd == '':
            kwd = '*'
        paths = glob.glob(str(self.data / f"pipe-{kwd}.json"))
        return [common.loadopt(path) for path in paths]

    def exec_pipe(self, title, opt):
        self.logger.info(f"exec_pipe: title={title}, opt={opt}")
        def _exec_pipe(title, opt, container):
            capture_stdout = True
            for i, cmd_title in enumerate(opt['pipe_cmd']):
                if cmd_title == '':
                    continue
                cmd_opt = self.load_cmd(cmd_title)
                if 'capture_stdout' in cmd_opt:
                    capture_stdout = cmd_opt['capture_stdout']
                else:
                    capture_stdout = True
            cmdline = self.raw_pipe(title, opt)['cmdlines']
            try:
                container['pipe_proc'] = subprocess.Popen(cmdline, shell=True, text=True, encoding='utf-8', 
                                                        stdout=(subprocess.PIPE if capture_stdout else None),
                                                        stderr=(subprocess.STDOUT if capture_stdout else None))
                while container['pipe_proc'].poll() is None:
                    time.sleep(0.1)
                if capture_stdout:
                    output = container['pipe_proc'].stdout.read()
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            if 'stdout_log' in opt and cmd_opt['stdout_log']:
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
                    ret = to_json(output)
                self.callback_return_pipe_exec_func(title, ret)
            except:
                self.callback_return_pipe_exec_func(title, output)
        th = threading.Thread(target=_exec_pipe, args=(title, opt, self.container))
        th.start()
        return dict(success='start_pipe')
    
    def callback_return_pipe_exec_func(self, title, output):
        raise NotImplementedError('callback_return_pipe_exec_func is not implemented.')
        
    def raw_pipe(self, title, opt):
        self.logger.info(f"raw_pipe: title={title}, opt={opt}")
        #pipe_outputs = []
        cmdlines = []
        for i, cmd_title in enumerate(opt['pipe_cmd']):
            if cmd_title == '':
                continue
            cmd_opt = self.load_cmd(cmd_title)
            if 'output_csv' in cmd_opt:
                del cmd_opt['output_csv']
            if i>0:
                cmd_opt['stdin'] = True
                if 'input_file' in cmd_opt:
                    del cmd_opt['input_file']
            cmd_output = self.raw_cmd(cmd_title, cmd_opt)
            #cmdline = cmd_output[0]['raw']
            #optjson = cmd_output[1]['raw']
            cmdlines.append(f'python -m {cmd_output[0]["raw"]}')
            #pipe_outputs.append(dict(no=i, title=cmd_title, cmdline=cmdline, optjson=optjson))
        #return pipe_outputs
        return dict(cmdlines=' | '.join(cmdlines))
        
    def save_pipe(self, title, opt):
        opt_path = self.data / f"pipe-{title}.json"
        self.logger.info(f"save_pipe: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)

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
        return version.__description__.split('\n')
        
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
                    host=q['host'], port=q['port'], password=q['password'], svname=q['svname'])
        for file in request.files.getall('files'):
            with tempfile.TemporaryDirectory() as tmpdir:
                upload_file:Path = Path(tmpdir) / file.raw_filename
                if not upload_file.parent.exists():
                    upload_file.parent.mkdir(parents=True)
                opt['svpath'] = str(svpath / Path(file.raw_filename).parent).replace('\\','/')
                opt['upload_file'] = str(upload_file)
                opt['capture_stdout'] = True
                file.save(opt['upload_file'])
                ret = self.exec_cmd("file_upload", opt, nothread=True)
                if len(ret) == 0 or 'success' not in ret[0]:
                    return str(ret)
        return 'upload success'
        #return f'upload {upload.filename}'
    
    def to_str(self, o):
        if type(o) == dict:
            return json.dumps(o, default=common.default_json_enc)
        return str(o)

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081):
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.logger.info(f"Start bottle web. allow_host={self.allow_host} listen_port={self.listen_port}")
        app = bottle.Bottle()

        @app.post('/get_mode_opt')
        def get_mode_opt():
            return self.to_str(self.get_mode_opt())

        @app.post('/get_cmd_opt')
        def get_cmd_opt():
            req = bottle.request.json
            mode = req['mode'] if 'mode' in req else None
            return self.to_str(self.get_cmd_opt(mode))

        @app.post('/get_opt_opt')
        def get_opt_opt(mode, cmd):
            req = bottle.request.json
            mode = req['mode'] if 'mode' in req else None
            cmd = req['cmd'] if 'cmd' in req else None
            return self.to_str(self.get_opt_opt(mode, cmd))

        @app.post('/list_cmd')
        def list_cmd():
            req = bottle.request.json
            kwd = req['kwd'] if 'kwd' in req else None
            return self.to_str(self.list_cmd(kwd))
        """
        @app.post('/save_cmd')
        def save_cmd():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            self.save_cmd(title, opt)

        @app.post('/load_cmd')
        def load_cmd():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            return self.load_cmd(title)

        @app.post('/del_cmd')
        def del_cmd():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            self.del_cmd(title)

        @app.post('/bbforce_cmd')
        def bbforce_cmd():
            self.bbforce_cmd()
        """
        @app.post('/exec_cmd')
        def exec_cmd():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            opt['capture_stdout'] = nothread = req['nothread'] if 'nothread' in req else True
            return self.to_str(self.exec_cmd(title, opt, nothread))
        """
        @app.post('/raw_cmd')
        def raw_cmd():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            return self.to_str(self.raw_cmd(title, opt))

        @app.post('/list_tree')
        def list_tree():
            req = bottle.request.json
            current_path = req['current_path'] if 'current_path' in req else None
            return self.list_tree(current_path)
        
        @app.post('/load_result')
        def load_result():
            req = bottle.request.json
            current_path = req['current_path'] if 'current_path' in req else None
            return self.load_result(current_path)

        @app.post('/load_capture')
        def load_capture():
            req = bottle.request.json
            current_path = req['current_path'] if 'current_path' in req else None
            return self.load_capture(current_path)

        @app.post('/list_pipe')
        def list_pipe():
            req = bottle.request.json
            kwd = req['kwd'] if 'current_path' in req else None
            return self.list_pipe(kwd)

        @app.post('/exec_pipe')
        def exec_pipe():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            return self.exec_pipe(title, opt)

        @app.post('/raw_pipe')
        def raw_pipe():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            return self.raw_pipe(title, opt)

        @app.post('/save_pipe')
        def save_pipe():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            opt = req['opt'] if 'opt' in req else None
            self.save_pipe(title, opt)

        @app.post('/del_pipe')
        def del_pipe():
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            self.del_pipe(title)

        @app.post('/load_pipe')
        def load_pipe(title):
            req = bottle.request.json
            title = req['title'] if 'title' in req else None
            return self.load_pipe(title)

        @app.get('/copyright')
        def copyright():
            return self.copyright()

        @app.get('/versions_iinfer')
        def versions_iinfer():
            return self.versions_iinfer()

        @app.get('/versions_used')
        def versions_used():
            return self.versions_used()
        
        @app.post('/filer/upload')
        def filer_upload():
            return self.filer_upload(bottle.request)
        """
        with open("iinfer_web.pid", mode="w", encoding="utf-8") as f:
            pid = os.getpid()
            f.write(str(pid))
            self.is_running = True
            server = _WSGIRefServer(host=self.allow_host, port=self.listen_port)
            th = threading.Thread(target=bottle.run, kwargs=dict(app=app, server=server))
            th.start()
            while self.is_running:
                time.sleep(0.01)
            server.srv.shutdown()

    def stop(self):
        with open("iinfer_web.pid", mode="r", encoding="utf-8") as f:
            pid = f.read()
            os.kill(int(pid), signal.CTRL_C_EVENT)
            self.logger.info(f"Stop bottle web. allow_host={self.allow_host} listen_port={self.listen_port}")

class _WSGIRefServer(bottle.WSGIRefServer):
    """
    runメソッドでWSGIRefServerを起動する際に、make_serverの戻り値をインスタンス変数にするためのクラス
    """
    def __init__(self, host='127.0.0.1', port=8080, **options):
        super().__init__(host, port, **options)

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
