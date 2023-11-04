from vp4onnx.app import common
from pathlib import Path
import base64
import logging
import json
import redis


class RedisClient(object):
    def __init__(self, logger: logging, redis_host: str = "localhost", redis_port: int = 6379):
        """
        Redisサーバーとの通信を行うクラス

        Args:
            logger (logging): ロガー
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
        """
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0)

    def __enter__(self):
        self.check_server()
        return self

    def __exit__(self, a, b, c):
        pass

    def check_server(self):
        """
        Redisサーバーにpingを送信し、応答があるか確認する
        """
        if not self.redis_cli.ping():
            self.terminate_server()
            self.logger.error(f"fail to ping redis-server")
            raise Exception("fail to ping redis-server")

    def _response(self, res_msg:list[str]):
        """
        Redisサーバーからの応答を解析する

        Args:
            res_msg (list[str]): Redisサーバーからの応答

        Returns:
            dict: 解析された応答
        """
        if len(res_msg) <= 0:
            self.logger.error(f"No response was received.")
            return {"error": f"No response was received."}
        res_json = json.loads(res_msg[0])
        if "error" in res_json:
            self.logger.error(res_msg[0])
        return res_json

    def deploy(self, name:str, img_width: int, img_height: int, model_onnx: Path, postprocess_py: Path, timeout:int = 60):
        """
        モデルをRedisサーバーにデプロイする

        Args:
            name (str): モデル名
            img_width (int): 画像の幅
            img_height (int): 画像の高さ
            model_onnx (Path): モデルのONNXファイルのパス
            postprocess_py (Path): 後処理スクリプトのパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        if " " in name:
            self.logger.error(f"Name contains whitespace.")
            return {"error": f"Name contains whitespace."}
        if img_width is None or img_width <= 0:
            self.logger.error(f"Image width is invalid.")
            return {"error": f"Image width is invalid."}
        if img_height is None or img_height <= 0:
            self.logger.error(f"Image height is invalid.")
            return {"error": f"Image height is invalid."}
        if not model_onnx.exists():
            self.logger.error(f"Model path {str(model_onnx)} does not exist")
            return {"error": f"Model path {str(model_onnx)} does not exist"}
        if not postprocess_py.exists():
            self.logger.error(f"Postprocess path {str(postprocess_py)} does not exist")
            return {"error": f"Postprocess path {str(postprocess_py)} does not exist"}
        with open(model_onnx, "rb") as mf, open(postprocess_py, "rb") as pf:
            model_onnx_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
            postprocess_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"deploy {reskey} {name} {img_width} {img_height} {model_onnx_bytes_b64} {postprocess_py_b64}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def undeploy(self, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーからアンデプロイする

        Args:
            name (str): モデル名
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"undeploy {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def start(self, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーで起動する

        Args:
            name (str): モデル名
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"start {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def stop(self, reskey:str, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーで停止する

        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"stop {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def predict(self, reskey:str, name:str, image: bytes = None, image_file:Path = None, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            image (bytes, optional): 画像データ. Defaults to None.
            image_file (Path, optional): 画像ファイルのパス. Defaults to None.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        if image is None and image_file is None:
            self.logger.error(f"Image and Image file is empty.")
            return {"error": f"Image and Image file is empty."}
        image_b64 = None
        if image_file is not None and not image_file.exists():
            with open(image_file, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode('utf-8')
        else:
            image_b64 = base64.b64encode(image).decode('utf-8')
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"predict {reskey} {name} {image_b64}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)
