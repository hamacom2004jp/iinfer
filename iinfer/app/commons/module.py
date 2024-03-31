from iinfer.app import common, predict, injection
from pathlib import Path
from typing import List, Dict, Any
import importlib.util
import inspect
import logging
import pkgutil


def load_custom_predict(custom_predict_py:Path, logger:logging.Logger) -> predict.Predict:
    """
    カスタム予測オブジェクトを読み込みます。

    Args:
        custom_predict_py (Path): カスタム予測オブジェクトのパス
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        iinfer.app.predict.Predict: 予測オブジェクト
    """
    spec = importlib.util.spec_from_file_location("iinfer.user.predict", custom_predict_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, predict.Predict):
            return obj(logger)
    raise BaseException(f"Predict class not found.({custom_predict_py})")

def load_predict(predict_type:str, logger:logging.Logger) -> predict.Predict:
    """
    指定された予測オブジェクトを読み込みます。

    Args:
        predict_type (str): 予測オブジェクトのモジュール名
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        predict.Predict: 予測オブジェクト
    """
    module = importlib.import_module("iinfer.app.predicts." + predict_type)
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and issubclass(obj, predict.Predict):
            return obj(logger)
    raise BaseException(f"Predict class not found.({predict_type})")

def load_before_injection_type(injection_type:List[str], config:Dict[str,Any], logger:logging.Logger) -> List[injection.BeforeInjection]:
    """
    指定された前処理オブジェクトを読み込みます。

    Args:
        injection_type (List[str]): 前処理オブジェクトのモジュール名
        config (Dict[str,Any]): 設定
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        List[injection.BeforeInjection]: 前処理オブジェクト
    """
    injections = []
    for t in injection_type:
        module = importlib.import_module("iinfer.app.injections." + t)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, injection.BeforeInjection):
                injections.append(obj(config, logger))
    if len(injections) > 0:
        return injections
    raise BaseException(f"BeforeInjection class not found.({injection_type})")

def load_after_injection_type(injection_type:List[str], config:Dict[str,Any], logger:logging.Logger) -> List[injection.AfterInjection]:
    """
    指定された後処理オブジェクトを読み込みます。

    Args:
        injection_type (List[str]): 後処理オブジェクトのモジュール名
        config (Dict[str,Any]): 設定
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        List[injection.AfterInjection]: 後処理オブジェクト
    """
    injections = []
    for t in injection_type:
        module = importlib.import_module("iinfer.app.injections." + t)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, injection.AfterInjection):
                injections.append(obj(config, logger))
    if len(injections) > 0:
        return injections
    raise BaseException(f"AfterInjection class not found.({injection_type})")

def load_before_injections(before_injection_py:List[Path], config:Dict[str,Any], logger:logging.Logger) -> List[injection.BeforeInjection]:
    """
    前処理オブジェクトを読み込みます。

    Args:
        before_injection_py (List[Path]): 前処理オブジェクトのパス
        config (Dict[str,Any]): 設定
        logger (logging.Logger): ロガー

    Returns:
        List[injection.BeforeInjection]: 前処理オブジェクト
    """
    injections = []
    for p in before_injection_py:
        spec = importlib.util.spec_from_file_location("iinfer.user.injection", p)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, injection.BeforeInjection):
                injections.append(obj(config, logger))
    return injections


def load_after_injections(after_injection_py:List[Path], config:Dict[str,Any], logger:logging.Logger) -> List[injection.AfterInjection]:
    """
    後処理オブジェクトを読み込みます。

    Args:
        after_injection_py (List[Path]): 後処理オブジェクトのパス
        config (Dict[str,Any]): 設定
        logger (logging.Logger): ロガー

    Returns:
        List[injection.AfterInjection]: 後処理オブジェクト
    """
    injections = []
    for p in after_injection_py:
        spec = importlib.util.spec_from_file_location("iinfer.user.injection", p)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, injection.AfterInjection):
                injections.append(obj(config, logger))
    return injections

def get_module_list(package_name) -> List[str]:
    """
    パッケージ内のモジュール名のリストを取得します。

    Args:
        package_name (str): パッケージ名

    Returns:
        List[str]: モジュール名のリスト
    """
    package = __import__(package_name, fromlist=[''])
    return [name for _, name, _ in pkgutil.iter_modules(package.__path__)]

for mod in get_module_list('iinfer.app.predicts'):
    if mod.startswith('__'):
        continue
    m = importlib.import_module("iinfer.app.predicts." + mod)
    site = None
    width = None
    height = None
    required_model_conf = False
    required_model_weight = False
    for f in dir(m):
        if f == 'SITE': site = getattr(m, f)
        elif f == 'IMAGE_WIDTH': width = getattr(m, f)
        elif f == 'IMAGE_HEIGHT': height = getattr(m, f)
        elif f == 'REQUIREd_MODEL_CONF': required_model_conf = getattr(m, f)
        elif f == 'REQUIREd_MODEL_WEIGHT': required_model_weight = getattr(m, f)
    common.BASE_MODELS[mod] = dict(site=site, image_width=width, image_height=height,
                                   required_model_conf=required_model_conf, required_model_weight=required_model_weight)

for mod in get_module_list('iinfer.app.injections'):
    if mod.startswith('__'):
        continue
    try:
        load_before_injection_type([mod], dict(), None)
        common.BASE_BREFORE_INJECTIONS[mod] = dict()
    except:
        pass
    try:
        load_after_injection_type([mod], dict(), None)
        common.BASE_AFTER_INJECTIONS[mod] = dict()
    except:
        pass
