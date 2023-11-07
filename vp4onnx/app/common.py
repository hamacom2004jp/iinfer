from io import BytesIO
from pathlib import Path
from PIL import Image
from tabulate import tabulate
import importlib.util
import logging
import logging.config
import random
import shutil
import string
import requests
import yaml
import time

PGM_DIR = Path("vp4onnx")
APP_ID = 'vp4onnx'

def load_config():
    logging.config.dictConfig(yaml.safe_load(open(PGM_DIR / "logconf.yml", encoding='UTF-8').read()))
    logger_client = logging.getLogger('client')
    logger_server = logging.getLogger('server')
    with open(PGM_DIR / 'config.yml') as f:
        config = yaml.safe_load(f)
    return logger_client, logger_server, config


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
