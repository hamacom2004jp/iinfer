from pathlib import Path
from iinfer.app import common
from typing import List
import base64
import cv2
import logging
import json
import numpy as np
import redis
import time


class Client(object):
    def __init__(self, logger: logging.Logger, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None):
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
        self.password = redis_password
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

    def _response(self, reskey:str, res_msg:List[str]):
        """
        Redisサーバーからの応答を解析する

        Args:
            reskey (str): Redisサーバーからの応答のキー
            res_msg (List[str]): Redisサーバーからの応答

        Returns:
            dict: 解析された応答
        """
        self.redis_cli.delete(reskey)
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

    def deploy(self, name:str, model_img_width: int, model_img_height: int, model_file: Path, predict_type: str, custom_predict_py: Path, timeout:int = 60):
        """
        モデルをRedisサーバーにデプロイする

        Args:
            name (str): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            model_file (Path): モデルファイルのパス
            predict_type (str): 推論方法のタイプ
            custom_predict_py (Path): 推論スクリプトのパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        if name is None or name == "":
            self.logger.error(f"name is empty.")
            return {"error": f"name is empty."}
        if " " in name:
            self.logger.error(f"name contains whitespace.")
            return {"error": f"name contains whitespace."}
        if model_file is None:
            self.logger.error(f"model_file or model_file is empty.")
            return {"error": f"model_file or model_file is empty."}
        if predict_type is None:
            self.logger.error(f"predict_type is empty.")
            return {"error": f"predict_type is empty."}
        if predict_type not in common.BASE_MODELS:
            self.logger.error(f"Unknown predict_type. {predict_type}")
            return {"error": f"predict_type is empty."}
        if model_img_width is None or model_img_width <= 0:
            model_img_width = common.BASE_MODELS[predict_type]['image_width']
        if model_img_height is None or model_img_height <= 0:
            model_img_height = common.BASE_MODELS[predict_type]['image_height']
        if not model_file.exists():
            self.logger.error(f"model_file {str(model_file)} does not exist")
            return {"error": f"model_file {str(model_file)} does not exist"}
        if predict_type == 'Custom':
            if custom_predict_py is None or not custom_predict_py.exists():
                self.logger.error(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                return {"error": f"custom_predict_py path {str(custom_predict_py)} does not exist"}
            with open(custom_predict_py, "rb") as pf:
                custom_predict_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
        else:
            custom_predict_py_b64 = None
        with open(model_file, "rb") as mf:
            model_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"deploy {reskey} {name} {model_img_width} {model_img_height} {predict_type} {model_file.name} {model_bytes_b64} {custom_predict_py_b64}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(reskey, res)

    def deploy_list(self, timeout:int = 60):
        """
        デプロイされたモデルのリストを取得する

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"deploy_list {reskey}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(reskey, res)

    def undeploy(self, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーからアンデプロイする

        Args:
            name (str): モデル名
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        if name is None or name == "":
            self.logger.error(f"name is empty.")
            return {"error": f"name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"undeploy {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(reskey, res)

    def start(self, name:str, model_provider:str = 'CPUExecutionProvider', use_track:bool=False, gpuid:int=None, timeout:int = 60):
        """
        モデルをRedisサーバーで起動する

        Args:
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            use_track (bool): Multi Object Trackerを使用するかどうか, by default False
            gpuid (int): GPU ID, by default None
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        if name is None or name == "":
            self.logger.error(f"name is empty.")
            return {"error": f"name is empty."}
        if model_provider is None or model_provider == "":
            self.logger.error(f"model_provider is empty.")
            return {"error": f"model_provider is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"start {reskey} {name} {model_provider} {use_track} {gpuid}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(reskey, res)

    def stop(self, name:str, timeout:int = 60):
        """
        モデルをRedisサーバーで停止する

        Args:
            name (str): モデル名
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        if name is None or name == "":
            self.logger.error(f"name is empty.")
            return {"error": f"name is empty."}
        reskey = common.random_string()
        self.redis_cli.rpush('server', f"stop {reskey} {name}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        return self._response(reskey, res)

    def predict(self, name:str, image = None, image_file:Path = None, image_type:str = 'jpg', output_image_file:Path = None, output_preview:bool=False, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            name (str): モデル名
            image (bytes, optional): 画像データ. Defaults to None. np.ndarray型の場合はデコードしない(RGBであること).
            image_file (Path, optional): 画像ファイルのパス. Defaults to None.
            image_type (str, optional): 画像の形式. Defaults to 'jpg'.
            output_image_file (Path, optional): 予測結果の画像ファイルのパス. Defaults to None.
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        if name is None or name == "":
            self.logger.error(f"name is empty.")
            return {"error": f"name is empty."}
        if image is None and image_file is None:
            self.logger.error(f"image and image_file is empty.")
            return {"error": f"image and image_file is empty."}
        npy_b64 = None
        if image_file is not None:
            if not image_file.exists():
                self.logger.error(f"Not found image_file. {image_file}.")
                return {"error": f"Not found image_file. {image_file}."}
            with open(image_file, "rb") as f:
                if image_type == 'npy':
                    img_npy = common.npyfile2npy(f)
                elif image_type == 'jpg' or image_type == 'png':
                    img_npy = common.imgfile2npy(f)
                else:
                    self.logger.error(f"image_type is invalid. {image_type}.")
                    return {"error": f"image_type is invalid. {image_type}."}
        else:
            if type(image) == np.ndarray:
                img_npy = image
            elif image_type == 'npy':
                img_npy = common.npybytes2npy(image)
            elif image_type == 'jpg' or image_type == 'png':
                img_npy = common.imgbytes2npy(image)
            else:
                self.logger.error(f"image_type is invalid. {image_type}.")
                return {"error": f"image_type is invalid. {image_type}."}

        npy_b64 = common.npy2b64str(img_npy)
        #img_npy2 = np.frombuffer(base64.b64decode(npy_b64), dtype='uint8').reshape(img_npy.shape)

        reskey = common.random_string()
        self.redis_cli.rpush('server', f"predict {reskey} {name} {npy_b64} {img_npy.shape[0]} {img_npy.shape[1]} {img_npy.shape[2] if len(img_npy.shape) > 2 else ''}")
        res = self.redis_cli.blpop([reskey], timeout=timeout)
        res_json = self._response(reskey, res)
        if "output_image" in res_json and "output_image_shape" in res_json:
            #byteio = BytesIO(base64.b64decode(res_json["output_image"]))
            #img_npy = np.load(byteio)
            img_npy = common.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
            if output_image_file is not None:
                common.npy2imgfile(img_npy, output_image_file=output_image_file, image_type=image_type)
            if output_preview:
                # RGB画像をBGR画像に変換
                img_npy = common.bgr2rgb(img_npy)
                try:
                    cv2.imshow('preview', img_npy)
                    cv2.waitKey(0)
                except KeyboardInterrupt:
                    pass
        return res_json

    def capture(self, name:str, output_image_file:Path = None, timeout:int = 60,
              capture_device = 0, capture_output_type:str = None, capture_frame_width:int = None, capture_frame_height:int = None, capture_fps:int = None, capture_output_fps:int = 10,
              output_preview:bool=False):
        """
        ビデオをキャプチャする

        Args:
            name (str): モデル名
            output_image_file (Path, optional): 予測結果の画像ファイルのパス. Defaults to None.
            timeout (int, optional): タイムアウト時間. Defaults to 60.
            capture_device (int or str): キャプチャするディバイス、ビデオデバイスのID, ビデオファイルのパス。rtspのURL. by default 0
            capture_output_type (str): キャプチャしたビデオの出力形式, by default None
            capture_frame_width (int): キャプチャするビデオのフレーム幅, by default None
            capture_frame_height (int): キャプチャするビデオのフレーム高さ, by default None
            capture_fps (int): キャプチャするビデオのフレームレート, by default None
            capture_output_fps (int): キャプチャするビデオのフレームレート, by default 30
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
        """
        cap = cv2.VideoCapture(capture_device)
        if capture_frame_width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
        if capture_frame_height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_frame_height)
        if capture_fps is not None:
            cap.set(cv2.CAP_PROP_FPS, capture_fps)
        try:
            interval = float(1 / capture_output_fps)
            while True:
                start = time.perf_counter()
                ret, frame = cap.read()
                if ret:
                    frame = common.bgr2rgb(frame)
                    res_json = self.predict(name, image=frame, output_image_file=output_image_file, timeout=timeout)
                    if "output_image" in res_json and "output_image_shape" in res_json:
                        img_npy = common.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                        if output_preview:
                            # RGB画像をBGR画像に変換
                            img_npy = common.bgr2rgb(img_npy)
                            cv2.imshow('preview', img_npy)
                            cv2.waitKey(1)
                    yield res_json
                else:
                    logging.error(f"Capture failed. devide_id={capture_device}", stack_info=True)
                    break
                end = time.perf_counter()
                if interval - (end - start) > 0:
                    time.sleep(interval - (end - start))

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt", exc_info=True)
        finally:
            cap.release()
