from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw
from pkg_resources import resource_string
from tabulate import tabulate
from typing import List, Tuple
import base64
import importlib.util
import json
import logging
import logging.config
import numpy as np
import os
import platform
import random
import shutil
import string
import requests
import subprocess
import time
import yaml

APP_ID = 'iinfer'

def load_config(mode:str):
    """
    指定されたモードのロガーと設定を読み込みます。

    Args:
        mode (str): モード名

    Returns:
        logger (logging.Logger): ロガー
        config (dict): 設定
    """
    log_config = yaml.safe_load(resource_string(APP_ID, "logconf.yml"))
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(mode)
    config = yaml.safe_load(resource_string(APP_ID, "config.yml"))
    return logger, config

def saveopt(opt:dict, opt_path:Path):
    """
    コマンドラインオプションをJSON形式でファイルに保存します。

    Args:
        opt (dict): コマンドラインオプション
        opt_path (Path): 保存先のファイルパス
    """
    if opt_path is None:
        return
    def _json_enc(o):
        if isinstance(o, Path):
            return str(o)
        raise TypeError(f"Type {type(o)} not serializable")
    with open(opt_path, 'w') as f:
        json.dump(opt, f, indent=4, default=_json_enc)

def loadopt(opt_path:str):
    """
    JSON形式のファイルからコマンドラインオプションを読み込みます。

    Args:
        opt_path (str): 読み込むファイルパス

    Returns:
        dict: 読み込んだコマンドラインオプション
    """
    if opt_path is None or not Path(opt_path).exists():
        return dict()
    with open(opt_path) as f:
        return json.load(f)

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False):
    """
    コマンドラインオプションから指定されたキーの値を取得します。

    Args:
        opt (dict): コマンドラインオプション
        key (str): キー
        preval (Any, optional): 優先する値. Defaults to None.
        defval (Any, optional): デフォルト値. Defaults to None.
        withset (bool, optional): キーが存在しない場合にデフォルト値を設定するかどうか. Defaults to False.

    Returns:
        Any: 取得した値
    """
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
    """
    ディレクトリを中間パスも含めて作成します。

    Args:
        dir_path (Path): 作成するディレクトリのパス

    Returns:
        Path: 作成したディレクトリのパス
    """
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def rmdirs(dir_path:Path):
    """
    ディレクトリをサブディレクトリ含めて削除します。

    Args:
        dir_path (Path): 削除するディレクトリのパス
    """
    shutil.rmtree(dir_path)

def load_custom_predict(custom_predict_py):
    """
    カスタム予測関数を読み込みます。

    Args:
        custom_predict_py ([type]): カスタム予測関数のパス

    Returns:
        [type]: カスタム予測関数
    """
    spec = importlib.util.spec_from_file_location("predict", custom_predict_py)
    predict = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predict)
    return predict.predict

def load_predict(predict_type:str):
    """
    指定された予測関数を読み込みます。

    Args:
        predict_type (str): 予測関数のパッケージ名

    Raises:
        BaseException: 指定された関数が見つからない場合

    Returns:
        [type]: 予測関数
    """
    module = importlib.import_module("iinfer.app.predicts." + predict_type)
    for func in dir(module):
        if func == 'predict':
            return getattr(module, func)
    raise BaseException(f"Function specified in {predict_type} not found.")

def random_string(size:int=16):
    """
    ランダムな文字列を生成します。

    Args:
        size (int, optional): 文字列の長さ. Defaults to 16.

    Returns:
        str: 生成された文字列
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

def print_format(data:dict, format:bool, tm:float):
    """
    データを指定されたフォーマットで出力します。

    Args:
        data (dict): 出力するデータ
        format (bool): フォーマットするかどうか
        tm (float): 処理時間
    """
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
    cls_EfficientNet_Lite4=dict(
        site='https://github.com/onnx/models/tree/main/vision/classification/efficientnet-lite4',
        image_width=224,
        image_height=224
    ),
    #Classification_Resnet=dict(
    #    site='https://github.com/onnx/models/tree/main/vision/classification/resnet',
    #    image_width=224,
    #    image_height=224
    #),
    det_YoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/yolov3',
        image_width=416,
        image_height=416
    ),
    det_TinyYoloV3=dict(
        site='https://github.com/onnx/models/tree/main/vision/object_detection_segmentation/tiny-yolov3',
        image_width=416,
        image_height=416
    ),
    det_YoloX=dict(
        site='https://github.com/hamacom2004jp/pth2onnx',
        image_width=640,
        image_height=640
    ),
    det_YoloX_Lite=dict(
        site='https://github.com/hamacom2004jp/pth2onnx',
        image_width=416,
        image_height=416
    )
)

def download_file(url:str, save_path:Path):
    """
    ファイルをダウンロードします。

    Args:
        url (str): ダウンロードするファイルのURL
        save_path (Path): 保存先のファイルパス

    Returns:
        Path: 保存したファイルのパス
    """
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(r.content)
    return save_path

def cmd(cmd:str, logger:logging.Logger):
    """
    コマンドを実行します。

    Args:
        cmd (str): 実行するコマンド
        logger (logging.Logger): ロガー

    Returns:
        Tuple[int, str]: コマンドの戻り値と出力
    """
    logger.debug(f"cmd:{cmd}")
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = None
    while proc.returncode is None:
        out = proc.stdout.readline()
        if out == b'' and proc.poll() is not None:
            break
        for enc in ['utf-8', 'cp932', 'utf-16', 'utf-16-le', 'utf-16-be']:
            try:
                output = out.decode(enc)
                if platform.system() == 'Windows':
                    output = output.rstrip()
                logger.debug(f"output:{output}")
                break
            except UnicodeDecodeError:
                pass

    return proc.returncode, output

def npyfile2npy(fp) -> np.ndarray:
    """
    npyファイルからndarrayを読み込みます。

    Args:
        fp ([type]): npyファイルのパス

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(fp)

def npybytes2npy(npy:bytes) -> np.ndarray:
    """
    バイト列からndarrayを読み込みます。

    Args:
        npy (bytes): ndarrayのバイト列

    Returns:
        np.ndarray: 読み込んだndarray
    """
    return np.load(BytesIO(npy))

def npy2b64str(npy:np.ndarray) -> str:
    """
    ndarrayをBase64エンコードした文字列を返します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        str: Base64エンコードされた文字列
    """
    return base64.b64encode(npy.tobytes()).decode('utf-8')

def npy2img(npy:np.ndarray) -> Image:
    """
    ndarrayをPILのImageオブジェクトに変換します。

    Args:
        npy (np.ndarray): ndarray

    Returns:
        Image: PILのImageオブジェクト
    """
    return Image.fromarray(npy)

def b64str2npy(b64str:str, shape:Tuple, dtype:str='uint8') -> np.ndarray:
    """
    Base64エンコードされた文字列からndarrayを復元します。

    Args:
        b64str (str): Base64エンコードされた文字列
        shape (tuple): ndarrayの形状
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: 復元したndarray
    """
    return np.frombuffer(base64.b64decode(b64str), dtype=dtype).reshape(shape)

def npy2imgfile(npy, output_image_file:Path=None, image_type:str='jpg') -> None:
    """
    ndarrayを画像bytesに変換しoutput_image_fileに保存します。
    output_image_fileが省略された場合は保存されません

    Args:
        npy ([type]): ndarray
        output_image_file (Path): 保存先の画像ファイルパス
    """
    image = Image.fromarray(npy)
    img_byte = img2byte(image, format=image_type)
    if output_image_file is not None:
        with open(output_image_file, 'wb') as f:
            f.write(img_byte)
    return img_byte

def bgr2rgb(npy:np.ndarray) -> np.ndarray:
    """
    BGRのndarrayをRGBに変換します。

    Args:
        npy (np.ndarray): BGRのndarray

    Returns:
        np.ndarray: RGBのndarray
    """
    return npy[..., ::-1]


def imgbytes2npy(img:bytes, dtype:str='uint8') -> np.ndarray:
    """
    画像のバイト列をndarrayに変換します。

    Args:
        img (bytes): 画像のバイト列
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(BytesIO(img))
    return np.array(img, dtype=dtype)

def imgfile2npy(fp, dtype:str='uint8') -> np.ndarray:
    """
    画像ファイルをndarrayに変換します。

    Args:
        fp ([type]): 画像ファイルのパス
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    img = Image.open(fp)
    return np.array(img, dtype=dtype)

def img2npy(image:Image, dtype:str='uint8') -> np.ndarray:
    """
    PILのImageオブジェクトをndarrayに変換します。

    Args:
        image (Image): PILのImageオブジェクト
        dtype (str, optional): ndarrayのデータ型. Defaults to 'uint8'.

    Returns:
        np.ndarray: ndarray
    """
    return np.array(image, dtype=dtype)

def img2byte(image:Image, format:str='JPEG') -> bytes:
    """
    画像をバイト列に変換します。

    Args:
        image (Image): PILのImageオブジェクト

    Returns:
        bytes: 画像のバイト列
    """
    with BytesIO() as buffer:
        image.save(buffer, format="JPEG")
        return buffer.getvalue()

def draw_boxes(image:Image, boxes:List[List[float]], scores:List[float], classes:List[int], ids:List[str] = None, labels:List[str] = None, colors:List[Tuple[int]] = None):
    """
    画像にバウンディングボックスを描画します。

    Args:
        image (Image): 描画する画像
        boxes (List[List[float]]): バウンディングボックスの座標リスト
        scores (List[float]): 各バウンディングボックスのスコアリスト
        classes (List[int]): 各バウンディングボックスのクラスリスト
        labels (List[str], optional): クラスのラベルリスト. Defaults to None.
        colors (List[Tuple[int]], optional): クラスごとの色のリスト. Defaults to None.

    Returns:
        Image: バウンディングボックスが描画された画像
    """
    draw = ImageDraw.Draw(image)
    ids = ids if ids is not None else [None] * len(boxes)
    for box, score, cl, id in zip(boxes, scores, classes, ids):
        y1, x1, y2, x2 = box
        x1 = max(0, np.floor(x1 + 0.5).astype(int))
        y1 = max(0, np.floor(y1 + 0.5).astype(int))
        x2 = min(image.width, np.floor(x2 + 0.5).astype(int))
        y2 = min(image.height, np.floor(y2 + 0.5).astype(int))
        color = colors[cl] if colors is not None and cl in colors else make_color(str(int(cl)))
        
        draw.rectangle(((x1, y1), (x2, y2)), outline=color)

        label = labels[cl] if labels is not None else str(id) if id is not None else None
        if label is not None:
            draw.rectangle(((x1, y1), (x2, y1+10)), outline=color, fill=color)
            draw.text((x1, y1), label, fill='white')
    
    return image

def make_color(idstr:str) -> Tuple[int]:
    if len(idstr) < 3:
        idstr = idstr.zfill(3)
    return tuple([ord(c) * ord(c) % 256 for c in idstr[:3]])
    