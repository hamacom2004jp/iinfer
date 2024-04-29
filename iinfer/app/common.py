from pathlib import Path
from PIL import Image, ImageDraw
from pkg_resources import resource_string
from tabulate import tabulate
from typing import List, Tuple, Dict, Any
import cv2
import datetime
import logging
import logging.config
import json
import numpy as np
import os
import platform
import random
import shutil
import string
import re
import requests
import subprocess
import tempfile
import time
import yaml

APP_ID = 'iinfer'
HOME_DIR = Path(os.path.expanduser("~"))

def load_config(mode:str) -> Tuple[logging.Logger, dict]:
    """
    指定されたモードのロガーと設定を読み込みます。

    Args:
        mode (str): モード名

    Returns:
        logger (logging.Logger): ロガー
        config (dict): 設定
    """
    log_config = yaml.safe_load(resource_string(APP_ID, f"logconf_{mode}.yml"))
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(mode)
    config = yaml.safe_load(resource_string(APP_ID, "config.yml"))
    return logger, config

def default_json_enc(o) -> Any:
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.float32):
        return float(o)
    if isinstance(o, np.int64):
        return int(o)
    if isinstance(o, np.int32):
        return int(o)
    if isinstance(o, np.intc):
        return int(o)
    if isinstance(o, Path):
        return str(o)
    if isinstance(o, tempfile._TemporaryFileWrapper):
        return str(o)
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError(f"Type {type(o)} not serializable")

def saveopt(opt:dict, opt_path:Path) -> None:
    """
    コマンドラインオプションをJSON形式でファイルに保存します。

    Args:
        opt (dict): コマンドラインオプション
        opt_path (Path): 保存先のファイルパス
    """
    if opt_path is None:
        return
    with open(opt_path, 'w') as f:
        json.dump(opt, f, indent=4, default=default_json_enc)

def loadopt(opt_path:str) -> dict:
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

def getopt(opt:dict, key:str, preval=None, defval=None, withset=False) -> any:
    """
    コマンドラインオプションから指定されたキーの値を取得します。

    Args:
        opt (dict): 読み込んだコマンドラインオプション
        key (str): キー
        preval (Any, optional): 引数で指定されたコマンドラインオプション. Defaults to None.
        defval (Any, optional): デフォルト値. Defaults to None.
        withset (bool, optional): optに引数のコマンドラインオプションを設定するかどうか. Defaults to False.

    Returns:
        Any: 取得した値
    """
    if preval is not None:
        v = preval
        if isinstance(preval, dict):
            v = preval.get(key, None)
        if (v is None or not v) and key in opt:
            v = opt[key]
        elif v is None or not v:
            v = defval
        if withset:
            opt[key] = v
        return v
    if key in opt:
        return opt[key]
    else:
        if withset:
            opt[key] = defval
        return defval

def safe_fname(fname:str) -> str:
    """
    ファイル名に使えない文字を置換します。

    Args:
        fname (str): ファイル名

    Returns:
        str: 置換後のファイル名
    """
    return re.sub('[\s:\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]', '_',str(fname))

def check_fname(fname:str) -> bool:
    """
    ファイル名に使えない文字が含まれているかどうかをチェックします。

    Args:
        fname (str): ファイル名

    Returns:
        bool: Trueの場合は使えない文字が含まれている
    """
    return re.search('[\s:\\\\/,\.\?\#\$\%\^\&\!\@\*\~\|\<\>\(\)\{\}\[\]\'\"\`]',str(fname)) is not None

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

def random_string(size:int=16):
    """
    ランダムな文字列を生成します。

    Args:
        size (int, optional): 文字列の長さ. Defaults to 16.

    Returns:
        str: 生成された文字列
    """
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

def print_format(data:dict, format:bool, tm:float, output_json:str=None, output_json_append:bool=False, stdout:bool=True, tablefmt:str='github'):
    """
    データを指定されたフォーマットで出力します。

    Args:
        data (dict): 出力するデータ
        format (bool): フォーマットするかどうか
        tm (float): 処理時間
        output_json (str, optional): JSON形式で出力するファイルパス. Defaults to None.
        output_json_append (bool, optional): JSON形式で出力するファイルパス. Defaults to False.
        stdout (bool, optional): 標準出力に出力するかどうか. Defaults to True.
        tablefmt (str, optional): テーブルのフォーマット. Defaults to 'github'.
    Returns:
        str: 生成された文字列
    """
    txt = ''
    if format:
        if 'success' in data and type(data['success']) == list:
            txt = tabulate(data['success'], headers='keys', tablefmt=tablefmt)
        elif 'success' in data and type(data['success']) == dict:
            txt = tabulate([data['success']], headers='keys', tablefmt=tablefmt)
        elif type(data) == list:
            txt = tabulate(data, headers='keys', tablefmt=tablefmt)
        else:
            txt = tabulate([data], headers='keys', tablefmt=tablefmt)
        if stdout:
            try:
                print(txt)
                print(f"{time.time() - tm:.03f} seconds.")
            except BrokenPipeError:
                pass
    else:
        try:
            if type(data) == dict:
                txt = json.dumps(data, default=default_json_enc, ensure_ascii=False)
            else:
                txt = data
        except:
            txt = data
        if stdout:
            try:
                print(txt)
            except BrokenPipeError:
                pass
    if output_json is not None:
        try:
            with open(output_json, 'a' if output_json_append else 'w', encoding='utf-8') as f:
                json.dump(data, f, default=default_json_enc, ensure_ascii=False)
                print('', file=f)
        except Exception as e:
            pass
    return txt

BASE_MODELS = {}
BASE_BREFORE_INJECTIONS = {}
BASE_AFTER_INJECTIONS = {}

def download_file(url:str, save_path:Path) -> Path:
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

def cmd(cmd:str, logger:logging.Logger, strip:bool=False):
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
                if platform.system() == 'Windows' or strip:
                    output = output.rstrip()
                logger.debug(f"output:{output}")
                break
            except UnicodeDecodeError:
                pass

    return proc.returncode, output

def draw_segment(img_npy:np.ndarray, segment:np.ndarray, colors:List[Tuple[int]], nodraw:bool=False) -> np.ndarray:
    """
    画像にマスクを描画します。

    Args:
        img_npy (np.ndarray): 元画像
        segment (np.ndarray): セグメンテーションのクラスマップ
        colors (List[Tuple[int]]): クラスごとの色のリスト
        nodraw (bool, optional): 描画しない場合はTrue. Defaults to False.

    Returns:
        Image: マスクが描画された画像
    """
    img_npy = cv2.cvtColor(img_npy, cv2.COLOR_RGB2BGR)
    masked_image = np.zeros_like(img_npy)

    for c in np.unique(segment):
        color = colors[int(c)] if colors is not None else make_color(str(int(c)))
        m = segment == c
        r = np.where(m, color[0], 0).astype(np.uint8)
        g = np.where(m, color[1], 0).astype(np.uint8)
        b = np.where(m, color[2], 0).astype(np.uint8)
        mask = cv2.merge([r, g, b])
        masked_image = cv2.addWeighted(masked_image, 1, mask[0], 1, 0)
    img_npy = cv2.addWeighted(img_npy, 0.5, masked_image, 0.5, 0)
    img_npy = cv2.cvtColor(img_npy, cv2.COLOR_BGR2RGB)
    return img_npy

def draw_boxes(image:Image.Image, boxes:List[List[float]], scores:List[float], classes:List[int], ids:List[str]=None, labels:List[str]=None, colors:List[Tuple[int]]=None,
               nodraw:bool=False, nolookup:bool=False) -> Tuple[Image.Image, List[str]]:
    """
    画像にバウンディングボックスを描画します。

    Args:
        image (Image.Image): 描画する画像
        boxes (List[List[float]]): バウンディングボックスの座標リスト
        scores (List[float]): 各バウンディングボックスのスコアリスト
        classes (List[int]): 各バウンディングボックスのクラスリスト
        ids (List[str]): 各バウンディングボックスのIDリスト
        labels (List[str], optional): クラスのラベルリスト. Defaults to None.
        colors (List[Tuple[int]], optional): クラスごとの色のリスト. Defaults to None.
        nodraw (bool, optional): 描画しない場合はTrue. Defaults to False.
        nolookup (bool, optional): ラベル及び色をクラスIDから取得しない場合はTrue. Defaults to False.

    Returns:
        Image: バウンディングボックスが描画された画像
        List[str]: 各バウンディングボックスのラベルリスト
    """
    draw = ImageDraw.Draw(image)
    ids = ids if ids is not None else [None] * len(boxes)
    output_labels = []
    for i, (box, score, cl, id) in enumerate(zip(boxes, scores, classes, ids)):
        y1, x1, y2, x2 = box
        x1 = max(0, np.floor(x1 + 0.5).astype(int))
        y1 = max(0, np.floor(y1 + 0.5).astype(int))
        x2 = min(image.width, np.floor(x2 + 0.5).astype(int))
        y2 = min(image.height, np.floor(y2 + 0.5).astype(int))
        if not nolookup:
            color = colors[int(cl)] if colors is not None and len(colors) > cl else make_color(str(int(cl)))
            label = str(labels[int(cl)]) if labels is not None else str(id) if id is not None else None
        else:
            color = colors[i] if colors is not None and len(colors) > i else make_color(str(int(cl)))
            label = str(labels[i]) if labels is not None and len(labels) > i else None
        if not nodraw:
            if x2 - x1 > 0 and y2 - y1 > 0:
                draw.rectangle(((x1, y1), (x2, y2)), outline=color)
                if label is not None:
                    draw.rectangle(((x1, y1), (x2, y1+10)), outline=color, fill=color)
                    draw.text((x1, y1), label, tuple([int(255-c) for c in color]))
        output_labels.append(label)

    return image, output_labels

def make_color(idstr:str) -> Tuple[int]:
    if len(idstr) < 3:
        idstr = idstr.zfill(3)
    return tuple([ord(c) * ord(c) % 256 for c in idstr[:3]])
    