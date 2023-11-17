from io import BytesIO
from pathlib import Path
from PIL import Image
from vp4onnx.app import common
from vp4onnx.app import client
import base64
import cv2
import logging
import numpy as np
import time
import sys


class Capture(client.Client):
    def __init__(self, logger: logging.Logger, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None):
        """
        Captureクラスのコンストラクタ

        Args:
            logger (logging.Logger): ロガー
            redis_host (str): Redisホスト, by default "localhost"
            redis_port (int): Redisポート, by default 6379
            redis_password (str): Redisパスワード, by default None
        """
        super().__init__(logger, redis_host, redis_port, redis_password)

    def video(self, name:str, output_image_file:Path = None, image_type:str = 'jpg', timeout:int = 60,
              capture_devide_id:int = 0, capture_file:Path = None, capture_output_type:str = 'preview', capture_frame_width:int = None, capture_frame_height:int = None, capture_fps:int = None, capture_output_fps:int = 10):
        """
        ビデオをキャプチャする

        Args:
            name (str): モデル名
            output_image_file (Path, optional): 予測結果の画像ファイルのパス. Defaults to None.
            timeout (int, optional): タイムアウト時間. Defaults to 60.
            capture_devide_id (int): キャプチャするビデオデバイスのID, by default 0
            capture_file (Path): キャプチャするビデオファイルのパス。指定された場合capture_devide_idは無視されます, by default None
            capture_output_type (str): キャプチャしたビデオの出力形式, by default 'preview'
            capture_frame_width (int): キャプチャするビデオのフレーム幅, by default None
            capture_frame_height (int): キャプチャするビデオのフレーム高さ, by default None
            capture_fps (int): キャプチャするビデオのフレームレート, by default None
            capture_output_fps (int): キャプチャするビデオのフレームレート, by default 30
        """
        cap = cv2.VideoCapture(capture_file if capture_file is not None else capture_devide_id)
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
                    res_json = self.predict(name, image=frame, image_type='npy_array', output_image_file=output_image_file, timeout=timeout)
                    if capture_output_type == 'preview':
                        if "output_image" in res_json and "output_image_shape" in res_json:
                            img_npy = common.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                            cv2.imshow('preview', img_npy)
                            cv2.waitKey(1)
                    elif capture_output_type == 'stdout':
                        yield res_json
                else:
                    logging.error(f"Capture failed. devide_id={capture_devide_id}", stack_info=True)
                    break
                end = time.perf_counter()
                if interval - (end - start) > 0:
                    time.sleep(interval - (end - start))

        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt", exc_info=True)
        finally:
            cap.release()
