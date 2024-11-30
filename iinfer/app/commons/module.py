from cmdbox.app.commons import module
from iinfer.app import common as cmn, predict, train, injection
from pathlib import Path
from typing import List, Dict, Any, Tuple
import importlib.util
import inspect
import logging


def load_custom_predict(custom_predict_py:Path, logger:logging.Logger) -> predict.Predict:
    """
    カスタム推論オブジェクトを読み込みます。

    Args:
        custom_predict_py (Path): カスタム推論オブジェクトのパス
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        iinfer.app.predict.Predict: 推論オブジェクト
    """
    spec = importlib.util.spec_from_file_location("iinfer.user.predict", custom_predict_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, predict.Predict):
            width = getattr(module, 'IMAGE_WIDTH')
            height = getattr(module, 'IMAGE_HEIGHT')
            pred = obj(logger)
            pred.IMAGE_WIDTH = width
            pred.IMAGE_HEIGHT = height
            return pred
    raise BaseException(f"Predict class not found.({custom_predict_py})")

def load_custom_train(custom_train_py:Path, logger:logging.Logger) -> train.Train:
    """
    カスタム学習オブジェクトを読み込みます。

    Args:
        custom_train_py (Path): カスタム学習オブジェクトのパス
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        iinfer.app.train.Train: 学習オブジェクト
    """
    spec = importlib.util.spec_from_file_location("iinfer.user.train", custom_train_py)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, train.Train):
            return obj(logger)
    raise BaseException(f"Train class not found.({custom_train_py})")

def build_predict(predict_type:str, custom_predict_py:str, logger:logging.Logger) -> Tuple[bool, predict.Predict]:
    """
    推論オブジェクトを構築します。

    Args:
        predict_type (str): 推論オブジェクトの型
        custom_predict_py (str): カスタム推論オブジェクトのパス
        logger (logging.Logger): ロガー
    
    Returns:
        Tuple[bool, predict.Predict]: 成功した場合はTrueと推論オブジェクト、失敗した場合はFalseとエラーメッセージ
    """
    if predict_type == 'Custom':
        custom_predict_py = Path(custom_predict_py) if custom_predict_py is not None else None
        if custom_predict_py is None:
            logger.warning(f"predict_type is Custom but custom_predict_py is None.")
            return False, {"warn": f"predict_type is Custom but custom_predict_py is None."}
        if not custom_predict_py.exists():
            logger.warning(f"custom_predict_py path {str(custom_predict_py)} does not exist")
            return False, {"warn": f"custom_predict_py path {str(custom_predict_py)} does not exist"}
        predict_obj = load_custom_predict(custom_predict_py, logger)
    else:
        predict_obj = load_predict(predict_type, logger)
    return True, predict_obj

def build_train(train_type:str, custom_train_py:str, logger:logging.Logger) -> Tuple[bool, train.Train]:
    """
    学習オブジェクトを構築します。

    Args:
        train_type (str): 学習オブジェクトの型
        custom_train_py (str): カスタム学習オブジェクトのパス
        logger (logging.Logger): ロガー
    
    Returns:
        Tuple[bool, train.Train]: 成功した場合はTrueと学習オブジェクト、失敗した場合はFalseとエラーメッセージ
    """
    if train_type == 'Custom':
        custom_train_py = Path(custom_train_py) if custom_train_py is not None else None
        if custom_train_py is None:
            logger.warning(f"train_type is Custom but custom_train_py is None.")
            return False, {"warn": f"train_type is Custom but custom_train_py is None."}
        if not custom_train_py.exists():
            logger.warning(f"custom_train_py path {str(custom_train_py)} does not exist")
            return False, {"warn": f"custom_train_py path {str(custom_train_py)} does not exist"}
        train_obj = load_custom_train(custom_train_py, logger)
    else:
        train_obj = load_train(train_type, logger)
    return True, train_obj

def load_predict(predict_type:str, logger:logging.Logger) -> predict.Predict:
    """
    指定された推論オブジェクトを読み込みます。

    Args:
        predict_type (str): 推論オブジェクトのモジュール名
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        predict.Predict: 推論オブジェクト
    """
    module = importlib.import_module("iinfer.app.predicts." + predict_type)
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, predict.Predict):
            return obj(logger)
    raise BaseException(f"Predict class not found.({predict_type})")

def load_train(train_type:str, logger:logging.Logger) -> train.Train:
    """
    指定された学習オブジェクトを読み込みます。

    Args:
        train_type (str): 学習オブジェクトのモジュール名
        logger (logging.Logger): ロガー

    Raises:
        BaseException: 指定されたオブジェクトが見つからない場合

    Returns:
        train.Train: 学習オブジェクト
    """
    module = importlib.import_module("iinfer.app.trains." + train_type)
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, train.Train):
            return obj(logger)
    raise BaseException(f"Train class not found.({train_type})")

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
            if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, injection.BeforeInjection):
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
            if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, injection.AfterInjection):
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
            if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, injection.BeforeInjection):
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
            if hasattr(obj, "__module__") and obj.__module__ == module.__name__ and inspect.isclass(obj) and issubclass(obj, injection.AfterInjection):
                injections.append(obj(config, logger))
    return injections


for mod in module.get_module_list('iinfer.app.predicts'):
    if mod.startswith('__'):
        continue
    m = importlib.import_module("iinfer.app.predicts." + mod)
    site = None
    width = None
    height = None
    model_type = predict.Predict
    required_model_conf = False
    required_model_weight = False
    for f in dir(m):
        members = inspect.getmembers(m, inspect.isclass)
        for name, cls in members:
            if issubclass(cls, predict.Predict):
                model_type = cls
                break
        if f == 'SITE': site = getattr(m, f)
        elif f == 'IMAGE_WIDTH': width = getattr(m, f)
        elif f == 'IMAGE_HEIGHT': height = getattr(m, f)
        elif f == 'MODEL_TYPE': model_type = getattr(m, f)
        elif f == 'REQUIREd_MODEL_CONF': required_model_conf = getattr(m, f)
        elif f == 'REQUIREd_MODEL_WEIGHT': required_model_weight = getattr(m, f)
    cmn.BASE_MODELS[mod] = dict(site=site, image_width=width, image_height=height, model_type=model_type,
                                   required_model_conf=required_model_conf, required_model_weight=required_model_weight)

for mod in module.get_module_list('iinfer.app.trains'):
    if mod.startswith('__'):
        continue
    m = importlib.import_module("iinfer.app.trains." + mod)
    site = None
    model_type = train.Train
    for f in dir(m):
        members = inspect.getmembers(m, inspect.isclass)
        for name, cls in members:
            if issubclass(cls, train.Train):
                model_type = cls
                break
        if f == 'SITE': site = getattr(m, f)
    cmn.BASE_TRAIN_MODELS[mod] = dict(site=site, model_type=model_type)

for mod in module.get_module_list('iinfer.app.injections'):
    if mod.startswith('__'):
        continue
    try:
        load_before_injection_type([mod], dict(), None)
        cmn.BASE_BREFORE_INJECTIONS[mod] = dict()
    except:
        pass
    try:
        load_after_injection_type([mod], dict(), None)
        cmn.BASE_AFTER_INJECTIONS[mod] = dict()
    except:
        pass
