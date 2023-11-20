from motpy import Detection, MultiObjectTracker
from pathlib import Path
from PIL import Image
from vp4onnx.app import common
import base64
import logging
import json
import numpy as np
import onnxruntime as rt
import redis
import time


class Server(object):
    def __init__(self, data_dir: Path, logger: logging.Logger, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None):
        """
        Redisサーバーに接続し、クライアントからのコマンドを受信し実行する

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging): ロガー
            redis_host (str): Redisホスト名, by default "localhost"
            redis_port (int): Redisポート番号, by default 6379
            redis_password (str): Redisパスワード, by default None
        """
        self.data_dir = data_dir
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_cli = None
        self.sessions = {}
        self.is_running = False

    def __enter__(self):
        self.start_server()
        return self

    def __exit__(self, a, b, c):
        self.terminate_server()

    def start_server(self):
        """
        サーバー処理を開始する
        """
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=self.redis_password)
        try:
            self.redis_cli.ping()
            self.is_running = True
            self._run_server()
        except redis.exceptions.ConnectionError as e:
            self.is_running = False
            self.logger.error(f"fail to ping server. {e}")

    def _run_server(self):
        self.logger.info(f"start server")
        while self.is_running:
            try:
                # ブロッキングリストから要素を取り出す
                result = self.redis_cli.blpop('server', timeout=1)
                if result is None or len(result) <= 0:
                    time.sleep(1)
                    continue
                msg = result[1].decode().split(' ')
                if len(msg) <= 0:
                    time.sleep(1)
                    continue
                if msg[0] == 'deploy':
                    model_onnx = base64.b64decode(msg[6])
                    if msg[7] == 'None':
                        custom_predict_py = None
                    else:
                        custom_predict_py = base64.b64decode(msg[7])
                    self.deploy(msg[1], msg[2], int(msg[3]), int(msg[4]), msg[5], model_onnx, custom_predict_py)
                elif msg[0] == 'deploy_list':
                    self.deploy_list(msg[1])
                elif msg[0] == 'undeploy':
                    self.undeploy(msg[1], msg[2])
                elif msg[0] == 'start':
                    self.start(msg[1], msg[2], msg[3], (True if msg[4]=='True' else False))
                elif msg[0] == 'stop':
                    self.stop(msg[1], msg[2])
                elif msg[0] == 'predict':
                    #byteio = BytesIO(base64.b64decode(msg[3]))
                    #img_npy = np.load(byteio)
                    shape = [int(msg[4]), int(msg[5])]
                    if len(msg) > 6: shape.append(int(msg[6]))
                    img_npy = common.b64str2npy(msg[3], shape)
                    image = common.npy2img(img_npy)
                    self.predict(msg[1], msg[2], image)
            except redis.exceptions.TimeoutError:
                pass
            except redis.exceptions.ConnectionError as e:
                self.logger.error(f"Connection to the server was lost. {e}")
                self.is_running = False
                break
            except KeyboardInterrupt as e:
                self.is_running = False
                break

    def terminate_server(self):
        """
        サーバー処理を終了する
        """
        if self.redis_cli is not None:
            self.redis_cli.close()
            self.redis_cli = None
        self.logger.info(f"terminate server.")

    def _json_enc(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.float32):
            return float(o)
        if isinstance(o, np.int64):
            return int(o)
        if isinstance(o, np.intc):
            return int(o)
        raise TypeError(f"Type {type(o)} not serializable")
    
    def responce(self, reskey:str, result:dict):
        """
        処理結果をクライアントに返す

        Args:
            reskey (str): レスポンスキー
            result (dict): レスポンスデータ
        """
        self.redis_cli.rpush(reskey, json.dumps(result, default=self._json_enc))
        

    def deploy(self, reskey:str, name:str, model_img_width: int, model_img_height: int, predict_type:str, model_onnx: bytes, custom_predict_py: bytes):
        """
        モデルをデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            predict_type (str): 推論方法のタイプ
            model_onnx (bytes): モデルのONNX形式
            custom_predict_py (bytes): 推論のPythonスクリプト
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return
        if model_img_width is None or model_img_width <= 0:
            self.logger.warn(f"Image width is invalid.")
            self.responce(reskey, {"warn": f"Image width is invalid."})
            return
        if model_img_height is None or model_img_height <= 0:
            self.logger.warn(f"Image height is invalid.")
            self.responce(reskey, {"warn": f"Image height is invalid."})
            return

        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return
        if deploy_dir.exists():
            self.logger.warn(f"Could not be deployed. '{deploy_dir}' already exists")
            self.responce(reskey, {"warn": f"Could not be deployed. '{deploy_dir}' already exists"})
            return
        
        common.mkdirs(deploy_dir)
        with open(deploy_dir / "model.onnx", "wb") as f:
            f.write(model_onnx)
            self.logger.info(f"Save model.onnx to {str(deploy_dir)}")
        if custom_predict_py is not None:
            with open(deploy_dir / "custom_predict.py", "wb") as f:
                f.write(custom_predict_py)
                self.logger.info(f"Save custom_predict.py to {str(deploy_dir)}")
        with open(deploy_dir / "conf.json", "w") as f:
            conf = dict(model_img_width=model_img_width, model_img_height=model_img_height, predict_type=predict_type)
            json.dump(conf, f)
            self.logger.info(f"Save conf.json to {str(deploy_dir)}")
        self.responce(reskey, {"success": f"Save conf.json to {str(deploy_dir)}"})
        return

    def deploy_list(self, reskey:str):
        """
        デプロイされたモデルのリストを取得する

        Args:
            reskey (str): レスポンスキー

        Returns:
            dict: デプロイされたモデルのリスト
        """
        deploy_list = []
        for dir in self.data_dir.iterdir():
            if not dir.is_dir():
                continue
            conf_path = dir / "conf.json"
            with open(conf_path, "r") as cf:
                conf = json.load(cf)
                row = dict(name=dir.name, model_img_width=conf["model_img_width"], model_img_height=conf["model_img_height"],
                           predict_type=conf["predict_type"], model_onnx=(dir/"model.onnx").exists(), custom_predict=(dir/"custom_predict.py").exists(),
                           session=dir.name in self.sessions,
                           mot=dir.name in self.sessions and self.sessions[dir.name]['tracker'] is not None)
                deploy_list.append(row)
        self.responce(reskey, {"success": deploy_list})

    def undeploy(self, reskey:str, name:str):
        """
        モデルをアンデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return
        deploy_dir = self.data_dir / name
        common.rmdirs(deploy_dir)
        self.responce(reskey, {"success": f"Undeployed {name}. {str(deploy_dir)}"})
        return

    def start(self, reskey:str, name:str, model_provider:str, use_mot:bool):
        """
        モデルを読み込み、処理が実行できるようにする

        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            use_mot (bool): Multi Object Trackerを使用するかどうか, by default False
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return
        deploy_dir = self.data_dir / name
        model_path = deploy_dir / "model.onnx"
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return
        if not model_path.exists():
            self.logger.warn(f"Model path {str(model_path)} does not exist")
            self.responce(reskey, {"warn": f"Model path {str(model_path)} does not exist"})
            return
        conf_path = deploy_dir / "conf.json"
        if not conf_path.exists():
            self.logger.warn(f"Conf path {str(conf_path)} does not exist")
            self.responce(reskey, {"warn": f"Conf path {str(conf_path)} does not exist"})
            return
        with open(conf_path, "r") as cf:
            conf = json.load(cf)
            if conf["predict_type"] == 'Custom':
                custom_predict_py = deploy_dir / "custom_predict.py"
                if not custom_predict_py.exists():
                    self.logger.warn(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                    self.responce(reskey, {"warn": f"custom_predict_py path {str(custom_predict_py)} does not exist"})
                    return
                predictfunc = common.load_custom_predict(custom_predict_py)
            else:
                predictfunc = common.load_predict(conf["predict_type"])
            self.sessions[name] = dict(
                session=rt.InferenceSession(model_path, providers=[model_provider]),
                model_img_width=conf["model_img_width"],
                model_img_height=conf["model_img_height"],
                predictfunc=predictfunc,
                tracker=MultiObjectTracker(dt=0.1) if use_mot else None
            )
        self.logger.info(f"Successful start of {name} session.")
        self.responce(reskey, {"success": f"Successful start of {name} session."})
        return
    
    def stop(self, reskey:str, name:str):
        """
        モデルを開放する

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.responce(reskey, {"warn": f"{name} has not yet started a session."})
            return
        #self.sessions[name]['session'].close()
        del self.sessions[name]
        self.logger.info(f"Successful stop of {name} session.")
        self.responce(reskey, {"success": f"Successful stop of {name} session."})
        return

    def predict(self, reskey:str, name:str, image: Image):
        """
        クライアントから送られてきた画像の推論を行う。

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            img_npy (np.array): 推論する画像データ
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return
        if image is None:
            self.logger.warn(f"img_npy is empty.")
            self.responce(reskey, {"warn": f"img_npy is empty."})
            return
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.responce(reskey, {"warn": f"{name} has not yet started a session."})
            return
        session = self.sessions[name]
        try:
            # ONNX Runtimeで推論を実行
            predictfunc = session['predictfunc']
            outputs, output_image = predictfunc(session['session'], session['model_img_width'], session['model_img_height'], image, labels=None, colors=None)
            if output_image is not None:
                if session['tracker'] is not None:
                    if 'output_boxes' in outputs and 'output_scores' in outputs and 'output_classes' in outputs:
                        detections = [Detection(box, score, cls) for box, score, cls in zip(outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'])]
                        session['tracker'].step(detections=detections)
                        tracks = session['tracker'].active_tracks()
                        outputs['output_tracks'] = [t.id for t in tracks]
                        output_image = common.draw_boxes(output_image, outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'], ids=outputs['output_tracks'])
                output_image_npy = common.img2npy(output_image)
                output_image_b64 = common.npy2b64str(output_image_npy)
                self.responce(reskey, {"success": outputs, "output_image": output_image_b64, "output_image_shape": output_image_npy.shape})
                return
            self.responce(reskey, {"success": outputs})
            return
        except Exception as e:
            self.logger.warn(f"Failed to run inference: {e}", exc_info=True)
            self.responce(reskey, {"warn": f"Failed to run inference: {e}"})
            return
