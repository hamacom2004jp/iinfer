from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
import importlib.util
import logging
import logging.config
import numpy as np
import random
import shutil
import string
import yaml

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

def resize_img(image:Image, to_w, to_h):
    '''resize image with unchanged aspect ratio using padding'''
    iw, ih = image.size
    scale = min(to_w/iw, to_h/ih)
    nw = int(iw*scale)
    nh = int(ih*scale)
    image = image.resize((nw,nh), Image.BICUBIC)
    new_image = Image.new('RGB', (to_w, to_h), (128,128,128))
    new_image.paste(image, ((to_w-nw)//2, (to_h-nh)//2))
    return new_image

def preprocess_img(img:bytes, model_img_width:int, model_img_height:int):
    image = Image.open(BytesIO(img))
    boxed_image = resize_img(image, model_img_width, model_img_height)
    image_data = np.array(boxed_image, dtype='float32')
    image_data /= 255.
    image_data = np.transpose(image_data, [2, 0, 1])
    image_data = np.expand_dims(image_data, 0)
    image_size = np.array([image.size[1], image.size[0]], dtype=np.float32).reshape(1, 2)
    return image_data, image_size, image

def draw_boxes(image:Image, boxes:list[list[float]], scores:list[float], classes:list[int], labels:list[str] = None, colors = None):
    draw = ImageDraw.Draw(image)
    for box, score, cl in zip(boxes, scores, classes):
        x, y, w, h = box
        top = max(0, np.floor(x + 0.5).astype(int))
        left = max(0, np.floor(y + 0.5).astype(int))
        right = min(image.width, np.floor(x + w + 0.5).astype(int))
        bottom = min(image.height, np.floor(y + h + 0.5).astype(int))
        color = colors[cl] if colors is not None else (255, 0, 0)
        draw.rectangle(((top, left), (right, bottom)), outline=color)

        label = labels[cl] if labels is not None else str(cl)
        draw.text((top, left), label, fill=(0, 0, 0))
    
    return image

def image_to_bytes(image:Image):
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return buffer.getvalue()
