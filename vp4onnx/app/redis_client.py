from vp4onnx.app import common
from pathlib import Path
import base64
import logging
import json
import redis


class RedisClient(object):
    def __init__(self, logger: logging, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None):
        """
        Redisサーバーとの通信を行うクラス

        Args:
            logger (logging): ロガー
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
        """
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=redis_password)

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
        if res_msg is None:
            self.logger.error(f"Response timed out.")
            return {"error": f"Response timed out."}
        if len(res_msg) <= 0:
            self.logger.error(f"No response was received.")
            return {"error": f"No response was received."}
        msg = res_msg[1].decode('utf-8')
        res_json = json.loads(msg)
        msg_json = res_json.copy()
        if "output_image" in msg_json:
            msg_json["output_image"] = "binary"
        if "error" in res_json:
            self.logger.error(str(msg_json))
        if "warn" in res_json:
            self.logger.warn(str(msg_json))
        if "success" in res_json:
            self.logger.info(str(msg_json))
        return res_json

    def deploy(self, name:str, model_img_width: int, model_img_height: int, model_onnx: Path, predict_type: str, custom_predict_py: Path, timeout:int = 60):
        """
        モデルをRedisサーバーにデプロイする

        Args:
            name (str): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            model_onnx (Path): モデルのONNXファイルのパス
            predict_type (str): 推論方法のタイプ
            custom_predict_py (Path): 推論スクリプトのパス
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
        if model_img_width is None or model_img_width <= 0:
            self.logger.error(f"Image width is invalid.")
            return {"error": f"Image width is invalid."}
        if model_img_height is None or model_img_height <= 0:
            self.logger.error(f"Image height is invalid.")
            return {"error": f"Image height is invalid."}
        if not model_onnx.exists():
            self.logger.error(f"Model path {str(model_onnx)} does not exist")
            return {"error": f"Model path {str(model_onnx)} does not exist"}
        if predict_type == 'Custom':
            if custom_predict_py is None or not custom_predict_py.exists():
                self.logger.error(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                return {"error": f"custom_predict_py path {str(custom_predict_py)} does not exist"}
            with open(custom_predict_py, "rb") as pf:
                custom_predict_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
        else:
            custom_predict_py_b64 = None
        with open(model_onnx, "rb") as mf:
            model_onnx_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"deploy {reskey} {name} {model_img_width} {model_img_height} {predict_type} {model_onnx_bytes_b64} {custom_predict_py_b64}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def deploy_list(self, timeout:int = 60):
        """
        デプロイされたモデルのリストを取得する

        Returns:
            dict: Redisサーバーからの応答
        """
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"deploy_list {reskey}")
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

    def start(self, name:str, model_provider:str = 'CPUExecutionProvider', timeout:int = 60):
        """
        モデルをRedisサーバーで起動する

        Args:
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.error(f"Name is empty.")
            return {"error": f"Name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"start {reskey} {name} {model_provider}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def stop(self, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーで停止する

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
        self.redis_cli.rpush('server', f"stop {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(res)

    def predict(self, name:str, image: bytes = None, image_file:Path = None, output_image_file:Path = None, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            name (str): モデル名
            image (bytes, optional): 画像データ. Defaults to None.
            image_file (Path, optional): 画像ファイルのパス. Defaults to None.
            output_image_file (Path, optional): 予測結果の画像ファイルのパス. Defaults to None.
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
        if image_file is not None:
            if not image_file.exists():
                self.logger.error(f"Not found Image file. {image_file}.")
                return {"error": f"Not found Image file. {image_file}."}
            with open(image_file, "rb") as f:
                image_b64 = base64.b64encode(f.read()).decode('utf-8')
        else:
            image_b64 = base64.b64encode(image).decode('utf-8')
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"predict {reskey} {name} {image_b64}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        res_json = self._response(res)
        if "output_image" in res_json and output_image_file is not None:
            with open(output_image_file, "wb") as f:
                f.write(base64.b64decode(res_json["output_image"]))
            base64.b64decode(res_json["output_image"])
        return res_json
