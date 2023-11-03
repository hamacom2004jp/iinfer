from pathlib import Path
import importlib.util
import logging
import logging.config
import traceback
import sys
import yaml


PGM_DIR = Path("vp4onnx")
APP_ID = 'vp4onnx'
APP_DATA_DIR = None
CONFIG = None
LOGGER = None
SESSION_NAME = None
SESSION = None
SESSION_IMGSIZE = None
SESSION_POSTFUNC = None

def load_config():
    logging.config.dictConfig(yaml.safe_load(open(PGM_DIR / "logconf.yml", encoding='UTF-8').read()))
    logger = logging.getLogger('vt_main')
    with open(PGM_DIR / 'config.yml') as f:
        config = yaml.safe_load(f)
    return logger, config

def mkdirs(dir_path:Path):
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
    if not dir_path.is_dir():
        raise BaseException(f"Don't make diredtory.({str(dir_path)})")
    return dir_path

def e_msg(e:Exception, logger):
    tb = sys.exc_info()[2]
    logger.error(traceback.format_exc())
    return e.with_traceback(tb)

def load_postprocess(file_path):
    spec = importlib.util.spec_from_file_location("postprocess", file_path)
    predict = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(predict)
    return predict.postprocess
