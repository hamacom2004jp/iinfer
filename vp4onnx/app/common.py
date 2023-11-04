from pathlib import Path
import importlib.util
import logging
import logging.config
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

def load_postprocess(file_path):
    spec = importlib.util.spec_from_file_location("postprocess", file_path)
    predict = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predict)
    return predict.postprocess

def random_string(size:int=16):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=size))

