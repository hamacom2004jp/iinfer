from fastapi import APIRouter, File, UploadFile
from vp4onnx.app import common
import cv2
import numpy as np
import onnxruntime as rt
import os
import json

router = APIRouter()

@router.post("/predict/deploy/{name}/{img_width}/{img_height}")
async def deploy(name:str, img_width: int, img_height: int, model_onnx: UploadFile = File(...), postprocess_py: UploadFile = File(...)):
    """
    モデルのデプロイを行う関数

    Args:
        name (str): デプロイするモデルの名前
        img_width (int): 画像の幅
        img_height (int): 画像の高さ
        model_onnx (UploadFile, optional): モデルのONNXファイル. Defaults to File(...).
        postprocess_py (UploadFile, optional): 後処理のPythonファイル. Defaults to File(...).

    Returns:
        dict: デプロイの結果を格納した辞書. 成功時は{"result": "success"}、失敗時は{"error": エラーメッセージ}が返される
    """
    if common.SESSION is not None:
        common.LOGGER.error(f"Session has already been started from {name}")
        return {"error": f"Session has already been started from {name}"}

    dir_path = common.mkdirs(common.APP_DATA_DIR / name)
    with open(dir_path / "model.onnx", "wb") as f:
        f.write(await model_onnx.read())
        common.LOGGER.info(f"Save model.onnx to {str(dir_path)}")
    with open(dir_path / "postprocess.py", "wb") as f:
        f.write(await postprocess_py.read())
        common.LOGGER.info(f"Save postprocess.py to {str(dir_path)}")
    with open(dir_path / "conf.json", "w") as f:
        conf = {"IMAGE_SIZE": (img_width, img_height)}
        json.dump(conf, f)
        common.LOGGER.info(f"Save conf.json to {str(dir_path)}")
    return {"result": "success"}

@router.post("/predict/start/{name}")
async def start(name:str):
    """
    ONNXモデルを読み込み、推論セッションを開始する。

    Args:
        name (str): モデル名

    Returns:
        dict: 推論セッションの開始結果。成功時は{"result": "success"}、失敗時は{"error": エラーメッセージ}が返される。
    """
    model_path = common.APP_DATA_DIR / name / "model.onnx"

    if not os.path.exists(model_path):
        common.LOGGER.error(f"Model path {str(model_path)} does not exist")
        return {"error": f"Model path {str(model_path)} does not exist"}

    if common.SESSION is not None:
        common.LOGGER.info(f"Close model.onnx from {common.SESSION_NAME}")
        common.SESSION.close()
    common.SESSION = rt.InferenceSession(model_path)
    common.SESSION_NAME = name
    with open(common.APP_DATA_DIR / name / "conf.json", "r") as f:
        conf = json.load(f)
        common.SESSION_IMGSIZE = conf["IMAGE_SIZE"]
    common.SESSION_POSTFUNC = common.load_postprocess(common.APP_DATA_DIR / name / "postprocess.py")
    common.LOGGER.info(f"Start model.onnx from {common.SESSION_NAME, str(model_path)}")
    return {"result": "success"}

@router.post("/predict/stop/{name}")
async def stop(name:str):
    """
    推論セッションを停止する関数。

    Parameters
    ----------
    name : str
        セッション名。

    Returns
    -------
    dict
        セッションの停止結果を示す辞書。以下のキーを持つ。
        - "error": エラーが発生した場合にエラーメッセージを持つ。
        - "result": セッションの停止が成功した場合に"success"を持つ。
    """
    if common.SESSION is None:
        common.LOGGER.error("Session has not been started yet")
        return {"error": "Session has not been started yet"}
    common.SESSION.close()
    common.SESSION = None
    common.SESSION_NAME = None
    common.SESSION_IMGSIZE = None
    common.SESSION_POSTFUNC = None
    common.LOGGER.info(f"Stop model.onnx")
    return {"result": "success"}

@router.post("/predict/image/{name}")
async def predict(name:str, image_file: UploadFile = File(...)):
    if common.SESSION is None:
        common.LOGGER.error("Session has not been started yet")
        return {"error": "Session has not been started yet"}
    try:
        contents = await image_file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        img = cv2.resize(img, common.SESSION_IMGSIZE)
        img_array = np.array(img).astype(np.float32)
        img_array = np.transpose(img_array, (2, 0, 1))
        img_array = np.expand_dims(img_array, axis=0)

    except Exception as e:
        common.LOGGER.error(f"Failed to read image file: {e}")
        return {"error": f"Failed to read image file: {e}"}
    try:
        # ONNX Runtimeで推論を実行
        outputs = common.SESSION.run(None, {"input": img_array})
    except Exception as e:
        common.LOGGER.error(f"Failed to run inference: {e}")
        return {"error": f"Failed to run inference: {e}"}
    
    try:
        # 推論結果を後処理
        outputs_postprocess = common.SESSION_POSTFUNC(outputs)
        return outputs_postprocess
    except Exception as e:
        common.LOGGER.error(f"Failed to run postprocess: {e}")
        return {"error": f"Failed to run postprocess: {e}"}

