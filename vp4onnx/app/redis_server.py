from vp4onnx.app import common
from pathlib import Path
import base64
import cv2
import logging
import json
import numpy as np
import onnxruntime as rt
import redis
import time


class RedisServer(object):
    def __init__(self, data_dir: Path, logger: logging, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Redisサーバーに接続し、クライアントからのコマンドを受信し実行する

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging): ロガー
            redis_host (str): Redisホスト名, by default "localhost"
            redis_port (int): Redisポート番号, by default 6379
        """
        self.data_dir = data_dir
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
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
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
        try:
            self.redis_cli.ping()
            self.is_running = True
            self._run_server()
        except redis.exceptions.ConnectionError:
            self.is_running = False
            self.logger.error(f"fail to ping redis-server")

    def _run_server(self):
        self.logger.info(f"start redis-server")
        while self.is_running:
            try:
                # ブロッキングリストから要素を取り出す
                result = self.redis_cli.blpop('server', timeout=1)
                if result is None or len(result) <= 0:
                    time.sleep(1)
                    continue
                msg = result[0].decode().split(' ')
                if len(msg) <= 0:
                    time.sleep(1)
                    continue
                if msg[0] == 'deploy':
                    model_onnx = base64.b64decode(msg[5])
                    postprocess_py = base64.b64decode(msg[6])
                    self.deploy(msg[1], msg[2], int(msg[3]), int(msg[4]), model_onnx, postprocess_py)
                elif msg[0] == 'undeploy':
                    self.undeploy(msg[1], msg[2])
                elif msg[0] == 'start':
                    self.start(msg[1], msg[2])
                elif msg[0] == 'stop':
                    self.stop(msg[1], msg[2])
                elif msg[0] == 'predict':
                    image = base64.b64decode(msg[3])
                    self.predict(msg[1], msg[2], image)
            except redis.exceptions.TimeoutError:
                pass
            except redis.exceptions.ConnectionError:
                self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)
                time.sleep(1)
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

    def responce(self, reskey:str, result:dict):
        """
        処理結果をクライアントに返す

        Args:
            reskey (str): レスポンスキー
            result (dict): レスポンスデータ
        """
        self.redis_cli.rpush(reskey, json.dumps(result))

    def deploy(self, reskey:str, name:str, img_width: int, img_height: int, model_onnx: bytes, postprocess_py: bytes):
        """
        モデルをデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            img_width (int): 画像の幅
            img_height (int): 画像の高さ
            model_onnx (bytes): モデルのONNX形式
            postprocess_py (bytes): ポストプロセスのPythonスクリプト
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            self.responce(reskey, {"error": f"Name is empty."})
            return
        if img_width is None or img_width <= 0:
            self.logger.error(f"Image width is invalid.")
            self.responce(reskey, {"error": f"Image width is invalid."})
            return
        if img_height is None or img_height <= 0:
            self.logger.error(f"Image height is invalid.")
            self.responce(reskey, {"error": f"Image height is invalid."})
            return

        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.error(f"{name} has already started a session.")
            self.responce(reskey, {"error": f"{name} has already started a session."})
            return
        if deploy_dir.exists():
            self.logger.error(f"Could not be deployed. '{deploy_dir}' already exists")
            self.responce(reskey, {"error": f"Could not be deployed. '{deploy_dir}' already exists"})
            return
        
        common.mkdirs(deploy_dir)
        with open(deploy_dir / "model.onnx", "wb") as f:
            f.write(model_onnx)
            self.logger.info(f"Save model.onnx to {str(deploy_dir)}")
        with open(deploy_dir / "postprocess.py", "wb") as f:
            f.write(postprocess_py)
            self.logger.info(f"Save postprocess.py to {str(deploy_dir)}")
        with open(deploy_dir / "conf.json", "w") as f:
            conf = {"IMAGE_SIZE": (img_width, img_height)}
            json.dump(conf, f)
            self.logger.info(f"Save conf.json to {str(deploy_dir)}")
        self.responce(reskey, {"success": f"Save conf.json to {str(deploy_dir)}"})
        return

    def undeploy(self, reskey:str, name:str):
        """
        モデルをアンデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            self.responce(reskey, {"error": f"Name is empty."})
            return
        if name in self.sessions:
            self.logger.error(f"{name} has already started a session.")
            self.responce(reskey, {"error": f"{name} has already started a session."})
            return
        deploy_dir = self.data_dir / name
        common.rmdirs(deploy_dir)
        self.responce(reskey, {"success": f"Undeployed {name}. {str(deploy_dir)}"})
        return

    def start(self, reskey:str, name:str):
        """
        モデルを読み込み、処理が実行できるようにする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            self.responce(reskey, {"error": f"Name is empty."})
            return
        deploy_dir = self.data_dir / name
        model_path = deploy_dir / "model.onnx"
        if name in self.sessions:
            self.logger.error(f"{name} has already started a session.")
            self.responce(reskey, {"error": f"{name} has already started a session."})
            return
        if not model_path.exists():
            self.logger.error(f"Model path {str(model_path)} does not exist")
            self.responce(reskey, {"error": f"Model path {str(model_path)} does not exist"})
            return
        conf_path = deploy_dir / "conf.json"
        if not conf_path.exists():
            self.logger.error(f"Conf path {str(conf_path)} does not exist")
            self.responce(reskey, {"error": f"Conf path {str(conf_path)} does not exist"})
            return
        post_path = deploy_dir / "postprocess.py"
        if not post_path.exists():
            self.logger.error(f"Postprocess path {str(post_path)} does not exist")
            self.responce(reskey, {"error": f"Postprocess path {str(post_path)} does not exist"})
            return
        with open(conf_path, "r") as cf, open(post_path, "r") as pf:
            conf = json.load(cf)
            postfunc = common.load_postprocess(post_path)
            self.sessions[name] = dict(
                session=rt.InferenceSession(model_path),
                img_size=conf["IMAGE_SIZE"],
                postfunc=postfunc
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
            self.logger.error(f"Name is empty.")
            self.responce(reskey, {"error": f"Name is empty."})
            return
        if name not in self.sessions:
            self.logger.error(f"{name} has not yet started a session.")
            self.responce(reskey, {"error": f"{name} has not yet started a session."})
            return
        self.sessions[name]['session'].close()
        del self.sessions[name]
        self.logger.info(f"Successful stop of {name} session.")
        self.responce(reskey, {"success": f"Successful stop of {name} session."})
        return

    def predict(self, reskey:str, name:str, image: bytes):
        """
        クライアントから送られてきた画像の推論を行う。

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            image (bytes): 推論する画像データ
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            self.responce(reskey, {"error": f"Name is empty."})
            return
        if image is None or image == "":
            self.logger.error(f"Image is empty.")
            self.responce(reskey, {"error": f"Image is empty."})
            return
        if name not in self.sessions:
            self.logger.error(f"{name} has not yet started a session.")
            self.responce(reskey, {"error": f"{name} has not yet started a session."})
            return
        try:
            nparr = np.frombuffer(image, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            img = cv2.resize(img, self.sessions[name]['img_size'])
            img_array = np.array(img).astype(np.float32)
            img_array = np.transpose(img_array, (2, 0, 1))
            img_array = np.expand_dims(img_array, axis=0)
        except Exception as e:
            common.LOGGER.error(f"Failed to read image file: {e}")
            self.responce(reskey, {"error": f"Failed to read image file: {e}"})
            return
        try:
            # ONNX Runtimeで推論を実行
            outputs = self.sessions[name]['session'].run(None, {"input": img_array})
        except Exception as e:
            common.LOGGER.error(f"Failed to run inference: {e}")
            self.responce(reskey, {"error": f"Failed to run inference: {e}"})
            return
        try:
            # 推論結果を後処理
            outputs_postprocess = self.sessions[name]['postfunc'](outputs)
            self.responce(reskey, {"success": outputs_postprocess})
        except Exception as e:
            common.LOGGER.error(f"Failed to run postprocess: {e}")
            self.responce(reskey, {"error": f"Failed to run postprocess: {e}"})
            return

