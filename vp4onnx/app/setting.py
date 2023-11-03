from voicetranslator.app import common
from pathlib import Path
import json


def load_setting(app_data_dir:Path):
    conf_dir = common.mkdirs(app_data_dir / 'config')
    file = conf_dir / 'setting.json'
    speacker_json = {}
    try:
        with open(file, "r", encoding="utf-8") as f:
            speacker_json = json.load(f)
    except:
        pass

    return speacker_json

def save_setting(app_data_dir:Path, settings:dict):
    conf_dir = common.mkdirs(app_data_dir / 'config')
    file = conf_dir / 'setting.json'
    try:
        with open(file, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        raise BaseException(f"Don't save speacker setting.({str(file)})") from e
