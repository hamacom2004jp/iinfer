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
    def __init__(self, logger:logging.Logger, redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server'):
        """
        Redisサーバーとの通信を行うクラス

        Args:
            logger (logging): ロガー
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): 推論サーバーのサービス名. Defaults to 'server'.
        """
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.password = redis_password
        if svname is None or svname == "":
            raise Exception("svname is empty.")
        self.svname = f"sv-{svname}"
        self.hbname = f"hb-{svname}"
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=redis_password)

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
        found = self.redis_cli.keys(self.hbname)
        if len(found) <= 0:
            self.logger.error(f"Server not found. svname={self.svname.split('-')[1]}")
            raise Exception(f"Server Not found. svname={self.svname.split('-')[1]}")

    def _proc(self, key, cmd:str, params:List[str], timeout:int = 60):
        """
        コマンドをRedisサーバーに送信し、応答を取得する

        Args:
            key (str): コマンドのキー
            cmd (str): コマンド
            params (List[str]): コマンドのパラメータ
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        try:
            self.check_server()
            reskey = common.random_string()
            self.redis_cli.rpush(key, f"{cmd} {reskey} {' '.join([str(p) for p in params])}")
            res = self.redis_cli.blpop([reskey], timeout=timeout)
            return self._response(reskey, res)
        except Exception as e:
            self.logger.error(f"fail to execute command. cmd={cmd}, params={params}, msg={e}", exc_info=True)
            return {"error": f"fail to execute command. cmd={cmd}, params={params}, msg={e}"}

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

    def deploy(self, name:str, model_img_width:int, model_img_height:int, model_file:Path, model_conf_file:List[Path], predict_type:str, custom_predict_py:Path,
               label_file:Path, color_file:Path, overwrite:bool, timeout:int = 60):
        """
        モデルをRedisサーバーにデプロイする

        Args:
            name (str): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            model_file (Path): モデルファイルのパス
            model_conf_file (List[Path]): モデル設定ファイルのパス
            predict_type (str): 推論方法のタイプ
            custom_predict_py (Path): 推論スクリプトのパス
            label_file (Path): ラベルファイルのパス
            color_file (Path): 色ファイルのパス
            overwrite (bool): モデルを上書きするかどうか
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
        if label_file is not None and not label_file.exists():
            self.logger.error(f"label_file {str(label_file)} does not exist")
            return {"error": f"label_file {str(label_file)} does not exist"}
        elif label_file is not None:
            with open(label_file, "rb") as lf:
                label_file_b64 = base64.b64encode(lf.read()).decode('utf-8')
        else:
            label_file_b64 = None
        if color_file is not None and not color_file.exists():
            self.logger.error(f"color_file {str(color_file)} does not exist")
            return {"error": f"color_file {str(color_file)} does not exist"}
        elif color_file is not None:
            with open(color_file, "rb") as cf:
                color_file_b64 = base64.b64encode(cf.read()).decode('utf-8')
        else:
            color_file_b64 = None

        with open(model_file, "rb") as mf:
            model_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
        if model_conf_file is not None:
            model_conf_bytes_b64 = []
            model_conf_file_name = []
            for cf in model_conf_file:
                if not cf.exists():
                    self.logger.error(f"model_conf_file {str(cf)} does not exist")
                    return {"error": f"model_conf_file {str(cf)} does not exist"}
                with open(cf, "rb") as f:
                    model_conf_bytes_b64.append(base64.b64encode(f.read()).decode('utf-8'))
                model_conf_file_name.append(cf.name)
            model_conf_bytes_b64 = ','.join(model_conf_bytes_b64)
            model_conf_file_name = ','.join(model_conf_file_name)
        else:
            model_conf_bytes_b64 = None
            model_conf_file_name = None
        res_json = self._proc(self.svname, 'deploy', [name, str(model_img_width), str(model_img_height), predict_type,
                                                   model_file.name, model_bytes_b64, model_conf_file_name, model_conf_bytes_b64, custom_predict_py_b64,
                                                   label_file_b64, color_file_b64, overwrite], timeout=timeout)
        return res_json

    def deploy_list(self, timeout:int = 60):
        """
        デプロイされたモデルのリストを取得する

        Returns:
            dict: Redisサーバーからの応答
        """
        if self.password is None or self.password == "":
            self.logger.error(f"password is empty.")
            return {"error": f"password is empty."}
        res_json = self._proc(self.svname, 'deploy_list', [], timeout=timeout)
        return res_json

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
        res_json = self._proc(self.svname, 'undeploy', [name], timeout=timeout)
        return res_json

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
        res_json = self._proc(self.svname, 'start', [name, model_provider, str(use_track), str(gpuid)], timeout=timeout)
        return res_json

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
        res_json = self._proc(self.svname, 'stop', [name], timeout=timeout)
        return res_json


    def stop_server(self, timeout:int = 60):
        res_json = self._proc(self.svname, 'stop_server', [], timeout=timeout)
        return res_json

    def predict(self, name:str, image = None, image_file:Path = None, image_type:str = 'jpeg', output_image_file:Path = None, output_preview:bool=False, nodraw:bool=False, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            name (str): モデル名
            image (np.ndarray | bytes, optional): 画像データ. Defaults to None. np.ndarray型の場合はデコードしない(RGBであること).
            image_file (Path, optional): 画像ファイルのパス. Defaults to None.
            image_type (str, optional): 画像の形式. Defaults to 'jpeg'.
            output_image_file (Path, optional): 予測結果の画像ファイルのパス. Defaults to None.
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
            nodraw (bool, optional): 描画フラグ. Defaults to False.
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
            if image_type == 'jpeg' or image_type == 'png' or image_type == 'bmp':
                with open(image_file, "rb") as f:
                    img_npy = common.imgfile2npy(f)
            elif image_type == 'capture':
                with open(image_file, "r", encoding='utf-8') as f:
                    res_list = []
                    for line in f:
                        capture_data = line.split(',')
                        t = capture_data[0]
                        img = capture_data[1]
                        h = int(capture_data[2])
                        w = int(capture_data[3])
                        c = int(capture_data[4])
                        if t == 'capture':
                            img_npy = common.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                        else:
                            img_npy = common.imgbytes2npy(common.b64str2bytes(img))
                        res_json = self.predict(name, image=img_npy, output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"capture file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
            elif image_type == 'output_json':
                with open(image_file, "r", encoding='utf-8') as f:
                    res_list = []
                    for line in f:
                        res_json = json.loads(line)
                        if not ("output_image" in res_json and "output_image_shape" in res_json):
                            self.logger.warn(f"image_file data is invalid. Not found output_image or output_image_shape key.")
                            continue
                        img_npy = common.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
                        res_json = self.predict(name, image=img_npy, output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"output_json file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
            else:
                self.logger.error(f"image_type is invalid. {image_type}.")
                return {"error": f"image_type is invalid. {image_type}."}
        else:
            if type(image) == np.ndarray:
                img_npy = image
            elif image_type == 'capture':
                capture_data = image.split(',')
                self.logger.info(f"capture_data={capture_data[1:]}")
                t = capture_data[0]
                img = capture_data[1]
                h = int(capture_data[2])
                w = int(capture_data[3])
                c = int(capture_data[4])
                if t == 'capture':
                    img_npy = common.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                else:
                    img_npy = common.imgbytes2npy(common.b64str2bytes(img))
            elif image_type == 'output_json':
                res_json = json.loads(image)
                if not ("output_image" in res_json and "output_image_shape" in res_json):
                    self.logger.error(f"image_file data is invalid. Not found output_image or output_image_shape key.")
                    return {"error": f"image_file data is invalid. Not found output_image or output_image_shape key."}
                img_npy = common.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
            elif image_type == 'jpeg' or image_type == 'png' or image_type == 'bmp':
                img_npy = common.imgbytes2npy(image)
            else:
                self.logger.error(f"image_type is invalid. {image_type}.")
                return {"error": f"image_type is invalid. {image_type}."}

        npy_b64 = common.npy2b64str(img_npy)
        #img_npy2 = np.frombuffer(base64.b64decode(npy_b64), dtype='uint8').reshape(img_npy.shape)

        res_json = self._proc(self.svname, 'predict', [name, npy_b64, str(nodraw), str(img_npy.shape[0]), str(img_npy.shape[1]), str(img_npy.shape[2] if len(img_npy.shape) > 2 else '')], timeout=timeout)
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
                    cv2.waitKey(1)
                except KeyboardInterrupt:
                    pass
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass
        return res_json

    def capture(self, capture_device='0', image_type:str='capture', capture_frame_width:int=None, capture_frame_height:int=None, capture_fps:int=1000, output_preview:bool=False):
        """
        ビデオをキャプチャしてその結果を出力する

        Args:
            capture_device (int or str): キャプチャするディバイス、ビデオデバイスのID, ビデオファイルのパス。rtspのURL. by default 0
            image_type (str, optional): 画像の形式. Defaults to 'capture'.
            capture_frame_width (int): キャプチャするビデオのフレーム幅, by default None
            capture_frame_height (int): キャプチャするビデオのフレーム高さ, by default None
            capture_fps (int): キャプチャするビデオのフレームレート, by default 10
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
        """
        if capture_device.isdecimal():
            capture_device = int(capture_device)
        cap = cv2.VideoCapture(capture_device)
        if capture_frame_width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
        if capture_frame_height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_frame_height)
        if capture_fps is not None:
            cap.set(cv2.CAP_PROP_FPS, capture_fps)
        try:
            interval = float(1 / capture_fps)
            while True:
                start = time.perf_counter()
                ret, frame = cap.read()
                if ret:
                    img_npy = common.bgr2rgb(frame)
                    if output_preview:
                        # RGB画像をBGR画像に変換
                        img_npy = common.bgr2rgb(img_npy)
                        cv2.imshow('preview', img_npy)
                        cv2.waitKey(1)
                    img_b64 = None
                    if image_type == 'capture' or image_type is None:
                        image_type = 'capture'
                        img_b64 = common.npy2b64str(img_npy)
                    else:
                        img_b64 = common.bytes2b64str(common.npy2imgfile(img_npy, image_type=image_type))
                    yield image_type, img_b64, img_npy.shape[0], img_npy.shape[1], img_npy.shape[2] if len(img_npy.shape) > 2 else -1
                else:
                    self.logger.error(f"Capture failed. devide_id={capture_device}", stack_info=True)
                    break
                end = time.perf_counter()
                if interval - (end - start) > 0:
                    time.sleep(interval - (end - start))

        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt", exc_info=True)
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass
            cap.release()
