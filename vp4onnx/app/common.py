from io import BytesIO
from pathlib import Path
from PIL import Image
from pkg_resources import resource_string
from tabulate import tabulate
import importlib.util
import json
import logging
import logging.config
import random
import shutil
import string
import requests
import subprocess
import time
import yaml

APP_ID = 'vp4onnx'

def load_config():
    log_config = yaml.safe_load(resource_string(APP_ID, "logconf.yml"))
    logging.config.dictConfig(log_config)
    logger_client = logging.getLogger('client')
    logger_server = logging.getLogger('server')
    logger_redis = logging.getLogger('redis')
    config = yaml.safe_load(resource_string(APP_ID, "config.yml"))
    return logger_client, logger_server, logger_redis, config

def saveopt(opt:dict, opt_path:Path):
    if opt_path is None:
        return
    def _json_enc(o):
        if isinstance(o, Path):
            return str(o)
        raise TypeError(f"Type {type(o)} not serializable")
    with open(opt_path, 'w') as f:
        json.dump(opt, f, indent=4, default=_json_enc)

def loadopt(opt_path:str):
    if opt_path is None or not Path(opt_path).exists():
        return dict()
    with open(opt_path) as f:
        return json.load(f)

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False):
    if preval is not None:
        v = preval
        if isinstance(preval, dict):
            v = preval.get(key, defval)
        if (v is None or not v) and key in opt:
            v = opt[key]
        if withset:
            opt[key] = v
        return v
    if key in opt:
        return opt[key]
    else:
        if withset:
            opt[key] = defval
        return defval

def mkdirs(dir_path:Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def rmdirs(dir_path:Path):
    shutil.rmtree(dir_path)

def load_custom_predict(custom_predict_py):
    spec = importlib.util.spec_from_file_location("predict", custom_predict_py)
    predict = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predict)
    return predict.predict

def load_predict(predict_type:str):
    module = importlib.import_module("vp4onnx.app.predicts." + predict_type)
    for func in dir(module):
        if func == 'predict':
            return getattr(module, func)
    raise BaseException(f"Function specified in {predict_type} not found.")

def random_string(size:int=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

def image_to_bytes(image:Image):
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return buffer.getvalue()

def print_format(data:dict, format:bool, tm:float):
    if format:
        if 'success' in data and type(data['success']) == list:
            print(tabulate(data['success'], headers='keys'))
        elif 'success' in data and type(data['success']) == dict:
            print(tabulate([data['success']], headers='keys'))
        elif type(data) == list:
            print(tabulate(data, headers='keys'))
        else:
            print(tabulate([data], headers='keys'))
        print(f"{time.time() - tm:.03f} seconds.")
    else:
        print(data)

BASE_MODELS = dict(
    Classification_EfficientNet_Lite4=dict(
        site='https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4',
        image_width=224,
        image_height=224
    ),
    #Classification_Resnet=dict(
    #    site='https://github.com/onnx/models/tree/main/vision/classification/resnet',
    #    image_width=224,
    #    image_height=224
    #),
    ObjectDetection_YoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3',
        image_width=416,
        image_height=416
    ),
    ObjectDetection_TinyYoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3',
        image_width=416,
        image_height=416
    )
)
    
def download_file(url:str, save_path:Path):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(r.content)
    return save_path

def cmd(cmd:str, logger:logging.Logger):
    logger.debug(f"cmd:{cmd}")
    #proc = subprocess.run(cmd, stdout=subprocess.PIPE)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = None
    while proc.returncode is None:
        out = proc.stdout.readline()
        if out == b'' and proc.poll() is not None:
            break
        for enc in ['utf-8', 'cp932', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                output = out.decode(enc).rstrip()
                logger.debug(f"output:{output}")
                break
            except UnicodeDecodeError:
                pass

    return proc.returncode, output
