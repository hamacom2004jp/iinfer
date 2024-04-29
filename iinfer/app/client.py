from pathlib import Path
from iinfer.app import common
from iinfer.app.commons import convert
from typing import List
import base64
import cv2
import datetime
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
        self.is_running = False

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
            self.is_running = True
            stime = time.time()
            while self.is_running:
                ctime = time.time()
                if ctime - stime > timeout:
                    raise Exception(f"Response timed out.")
                res = self.redis_cli.blpop([reskey], timeout=1)
                if res is None or len(res) <= 0:
                    time.sleep(1)
                    continue
                return self._response(reskey, res)
            raise KeyboardInterrupt(f"Stop command.")
        except KeyboardInterrupt as e:
            self.logger.error(f"Stop command. cmd={cmd}, params={params}", exc_info=True)
            return {"error": f"Stop command. cmd={cmd}, params={params}"}
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

    def deploy(self, name:str, model_img_width:int, model_img_height:int, model_file:Path, model_conf_file:List[Path], predict_type:str,
               custom_predict_py:Path, label_file:Path, color_file:Path,
               before_injection_conf:Path, before_injection_type:List[str], before_injection_py:List[Path],
               after_injection_conf:Path, after_injection_type:List[str], after_injection_py:List[Path], overwrite:bool, timeout:int = 60):
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
            before_injection_conf (Path): 推論前処理設定ファイルのパス
            before_injection_type (List[str]): 推論前処理タイプ
            before_injection_py (List[Path]): 推論前処理スクリプトのパス
            after_injection_type (List[str]): 推論後処理タイプ
            after_injection_conf (Path): 推論後処理設定ファイルのパス
            after_injection_py (List[Path]): 推論後処理スクリプトのパス
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
            return {"error": f"Unknown predict_type. {predict_type}"}
        if model_img_width is None or model_img_width <= 0:
            model_img_width = common.BASE_MODELS[predict_type]['image_width']
        if model_img_height is None or model_img_height <= 0:
            model_img_height = common.BASE_MODELS[predict_type]['image_height']
        if predict_type == 'Custom':
            if custom_predict_py is None or not custom_predict_py.exists():
                self.logger.error(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                return {"error": f"custom_predict_py path {str(custom_predict_py)} does not exist"}
            with open(custom_predict_py, "rb") as pf:
                custom_predict_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
        else:
            custom_predict_py_b64 = None
        if before_injection_type is not None and len(before_injection_type) > 0:
            for t in before_injection_type:
                if t not in common.BASE_BREFORE_INJECTIONS:
                    self.logger.error(f"Unknown before_injection_type. {t}")
                    return {"error": f"Unknown before_injection_type. {t}"}
            before_injection_type = ','.join(before_injection_type)
        if after_injection_type is not None and len(after_injection_type) > 0:
            for t in after_injection_type:
                if t not in common.BASE_AFTER_INJECTIONS:
                    self.logger.error(f"Unknown after_injection_type. {t}")
                    return {"error": f"Unknown after_injection_type. {t}"}
            after_injection_type = ','.join(after_injection_type)
        def _conf_b64(name:str, conf:Path):
            if conf is not None and not conf.exists():
                self.logger.error(f"{name} {conf} does not exist")
                return False, {"error": f"{name} {conf} does not exist"}
            elif conf is not None:
                with open(conf, "rb") as lf:
                    conf_b64 = base64.b64encode(lf.read()).decode('utf-8')
            else:
                conf_b64 = None
            return True, conf_b64
        ret, label_file_b64 = _conf_b64("label_file", label_file)
        if not ret: return label_file_b64
        ret, color_file_b64 = _conf_b64("color_file", color_file)
        if not ret: return color_file_b64
        ret, before_injection_conf_b64 = _conf_b64("before_injection_conf", before_injection_conf)
        if not ret: return before_injection_conf_b64
        ret, after_injection_conf_b64 = _conf_b64("after_injection_conf", after_injection_conf)
        if not ret: return after_injection_conf_b64
        if model_file is not None:
            if model_file.exists():
                with open(model_file, "rb") as mf:
                    model_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
            else:
                self.logger.error(f"model_file {model_file} does not exist")
                return {"error": f"model_file {model_file} does not exist"}
        else:
            model_bytes_b64 = None
        def _name_b64(aname:str, files:List[Path]):
            if files is not None:
                b64s = []
                names = []
                for p in files:
                    if not p.exists():
                        self.logger.error(f"{aname} {p} does not exist")
                        return False, {"error": f"{aname} {p} does not exist"}, None
                    with open(p, "rb") as f:
                        b64s.append(base64.b64encode(f.read()).decode('utf-8'))
                    names.append(p.name)
                return True, ','.join(names), ','.join(b64s)
            return True, None, None
        ret, model_conf_file_name, model_conf_bytes_b64 = _name_b64("model_conf_file", model_conf_file)
        if not ret: return model_conf_file_name
        ret, before_injection_py_name, before_injection_py_b64 = _name_b64("before_injection_py", before_injection_py)
        if not ret: return before_injection_py_name
        ret, after_injection_py_name, after_injection_py_b64 = _name_b64("after_injection_py", after_injection_py)
        if not ret: return after_injection_py_name
        res_json = self._proc(self.svname, 'deploy', [name, str(model_img_width), str(model_img_height), predict_type,
                                                   model_file.name, model_bytes_b64, model_conf_file_name, model_conf_bytes_b64,
                                                   custom_predict_py_b64, label_file_b64, color_file_b64,
                                                   before_injection_conf_b64, before_injection_type, before_injection_py_name, before_injection_py_b64,
                                                   after_injection_conf_b64, after_injection_type, after_injection_py_name, after_injection_py_b64, overwrite], timeout=timeout)
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

    def predict(self, name:str, image = None, image_file = None, image_file_enable:bool=True, image_type:str = 'jpeg', output_image_file:Path = None, output_preview:bool=False, nodraw:bool=False, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            name (str): モデル名
            image (np.ndarray | bytes, optional): 画像データ. Defaults to None. np.ndarray型の場合はデコードしない(RGBであること).
            image_file (str|file-like object, optional): 画像ファイルのパス. Defaults to None.
            image_file_enable (bool, optional): 画像ファイルを使用するかどうか. Defaults to True. image_fileがNoneでなく、このパラメーターがTrueの場合はimage_fileを使用する.
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
        if image_file is not None and image_file_enable:
            if type(image_file) == str:
                if not Path(image_file).exists():
                    self.logger.error(f"Not found image_file. {image_file}.")
                    return {"error": f"Not found image_file. {image_file}."}
            if image_type == 'jpeg' or image_type == 'png' or image_type == 'bmp':
                f = None
                try:
                    f = image_file if type(image_file) is not str else open(image_file, "rb")
                    img_npy = convert.imgfile2npy(f)
                finally:
                    if f is not None: f.close()
            elif image_type == 'capture':
                f = None
                try:
                    f = image_file if type(image_file) is not str else open(image_file, "r", encoding='utf-8')
                    res_list = []
                    for line in f:
                        if type(line) is bytes:
                            line = line.decode('utf-8').strip()
                        capture_data = line.split(',')
                        t = capture_data[0]
                        img = capture_data[1]
                        h = int(capture_data[2])
                        w = int(capture_data[3])
                        c = int(capture_data[4])
                        fn = Path(capture_data[5].strip())
                        if t == 'capture':
                            img_npy = convert.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                        else:
                            img_npy = convert.imgbytes2npy(convert.b64str2bytes(img))
                        res_json = self.predict(name, image=img_npy, image_file=fn, image_file_enable=False, output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"capture file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
                finally:
                    if f is not None: f.close()
            elif image_type == 'output_json':
                f = None
                try:
                    f = image_file if type(image_file) is not str else open(image_file, "r", encoding='utf-8')
                    res_list = []
                    for line in f:
                        res_json = json.loads(line)
                        if not ("output_image" in res_json and "output_image_shape" in res_json and "output_image_name" in res_json):
                            self.logger.warn(f"image_file data is invalid. Not found output_image or output_image_shape or output_image_name key.")
                            continue
                        img_npy = convert.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
                        res_json = self.predict(name, image=img_npy, image_file=Path(res_json['output_image_name']), image_file_enable=False,
                                                output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"output_json file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
                finally:
                    if f is not None: f.close()
            else:
                self.logger.error(f"image_type is invalid. {image_type}.")
                return {"error": f"image_type is invalid. {image_type}."}
        else:
            if type(image) == np.ndarray:
                img_npy = image
                if image_file is None: image_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.capture'
                image_file_enable = False
            elif image_type == 'capture':
                capture_data = image.split(',')
                #self.logger.info(f"capture_data={capture_data[1:]}")
                t = capture_data[0]
                img = capture_data[1]
                h = int(capture_data[2])
                w = int(capture_data[3])
                c = int(capture_data[4])
                if image_file is None: image_file = capture_data[5]
                image_file_enable = False
                if t == 'capture':
                    img_npy = convert.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                else:
                    img_npy = convert.imgbytes2npy(convert.b64str2bytes(img))
            elif image_type == 'output_json':
                res_json = json.loads(image)
                if not ("output_image" in res_json and "output_image_shape" in res_json and "output_image_name" in res_json):
                    self.logger.error(f"image_file data is invalid. Not found output_image or output_image_shape or output_image_name key.")
                    return {"error": f"image_file data is invalid. Not found output_image or output_image_shape or output_image_name key."}
                img_npy = convert.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
                if image_file is None: image_file = res_json["output_image_name"]
                image_file_enable = False
            elif image_type == 'jpeg' or image_type == 'png' or image_type == 'bmp':
                img_npy = convert.imgbytes2npy(image)
                if image_file is None: image_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.{image_type}'
                image_file_enable = False
            else:
                self.logger.error(f"image_type is invalid. {image_type}.")
                return {"error": f"image_type is invalid. {image_type}."}

        npy_b64 = convert.npy2b64str(img_npy)
        #img_npy2 = np.frombuffer(base64.b64decode(npy_b64), dtype='uint8').reshape(img_npy.shape)

        res_json = self._proc(self.svname, 'predict',
                              [name, npy_b64, str(nodraw), str(img_npy.shape[0]), str(img_npy.shape[1]),
                               str(img_npy.shape[2] if len(img_npy.shape) > 2 else '-1'), image_file], timeout=timeout)
        if "output_image" in res_json and "output_image_shape" in res_json:
            #byteio = BytesIO(base64.b64decode(res_json["output_image"]))
            #img_npy = np.load(byteio)
            img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
            if output_image_file is not None:
                exp = Path(output_image_file).suffix
                exp = exp[1:] if exp[0] == '.' else exp
                convert.npy2imgfile(img_npy, output_image_file=output_image_file, image_type=exp)
            if output_preview:
                # RGB画像をBGR画像に変換
                try:
                    cv2.imshow('preview', convert.bgr2rgb(img_npy))
                    cv2.waitKey(1)
                except KeyboardInterrupt:
                    pass
        return res_json
    
    def file_list(self, svpath:str, timeout:int = 60):
        """
        サーバー上のファイルリストを取得する

        Args:
            svpath (Path): サーバー上のファイルパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self._proc(self.svname, 'file_list', [str(svpath)], timeout=timeout)
        return res_json

    def file_mkdir(self, svpath:str, timeout:int = 60):
        """
        サーバー上にディレクトリを作成する

        Args:
            svpath (Path): サーバー上のディレクトリパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self._proc(self.svname, 'file_mkdir', [str(svpath)], timeout=timeout)
        return res_json
    
    def file_rmdir(self, svpath:str, timeout:int = 60):
        """
        サーバー上のディレクトリを削除する

        Args:
            svpath (Path): サーバー上のディレクトリパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self._proc(self.svname, 'file_rmdir', [str(svpath)], timeout=timeout)
        return res_json
    
    def file_download(self, svpath:str, download_file:Path, timeout:int = 60):
        """
        サーバー上のファイルをダウンロードする

        Args:
            svpath (Path): サーバー上のファイルパス
            download_file (Path): ローカルのファイルパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            bytes: ダウンロードファイルの内容
        """
        res_json = self._proc(self.svname, 'file_download', [str(svpath)], timeout=timeout)
        if "success" in res_json:
            if download_file is not None:
                if download_file.is_dir():
                    download_file = download_file / res_json["success"]["name"]
                if download_file.exists():
                    self.logger.error(f"download_file {download_file} already exists.")
                    return {"error": f"download_file {download_file} already exists."}
                with open(download_file, "wb") as f:
                    f.write(base64.b64decode(res_json["success"]["data"]))
                    del res_json["success"]["data"]
                    res_json["success"]["download_file"] = str(download_file.absolute())
        return res_json
    
    def file_upload(self, svpath:str, upload_file:Path, timeout:int = 60):
        """
        サーバー上にファイルをアップロードする

        Args:
            svpath (Path): サーバー上のファイルパス
            upload_file (Path): ローカルのファイルパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if upload_file is None:
            self.logger.error(f"upload_file is empty.")
            return {"error": f"upload_file is empty."}
        if not upload_file.exists():
            self.logger.error(f"input_file {upload_file} does not exist.")
            return {"error": f"input_file {upload_file} does not exist."}
        if upload_file.is_dir():
            self.logger.error(f"input_file {upload_file} is directory.")
            return {"error": f"input_file {upload_file} is directory."}
        with open(upload_file, "rb") as f:
            res_json = self._proc(self.svname, 'file_upload', [str(svpath), upload_file.name, base64.b64encode(f.read()).decode('utf-8')], timeout=timeout)
            return res_json

    def file_remove(self, svpath:str, timeout:int = 60):
        """
        サーバー上のファイルを削除する

        Args:
            svpath (Path): サーバー上のファイルパス
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self._proc(self.svname, 'file_remove', [str(svpath)], timeout=timeout)
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
            self.is_running = True
            while self.is_running:
                start = time.perf_counter()
                ret, frame = cap.read()
                output_image_name = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                if ret:
                    if capture_frame_width is not None and capture_frame_height is not None:
                        frame = cv2.resize(frame, (capture_frame_width, capture_frame_height), interpolation=cv2.INTER_NEAREST)
                    img_npy = convert.bgr2rgb(frame)
                    if output_preview:
                        # RGB画像をBGR画像に変換
                        cv2.imshow('preview', convert.bgr2rgb(img_npy))
                        cv2.waitKey(1)
                    img_b64 = None
                    if image_type == 'capture' or image_type is None:
                        image_type = 'capture'
                        img_b64 = convert.npy2b64str(img_npy)
                    else:
                        img_b64 = convert.bytes2b64str(convert.npy2imgfile(img_npy, image_type=image_type))
                    output_image_name = f"{output_image_name}.{image_type}"
                    yield image_type, img_b64, img_npy.shape[0], img_npy.shape[1], img_npy.shape[2] if len(img_npy.shape) > 2 else -1, output_image_name
                else:
                    self.logger.error(f"Capture failed. devide_id={capture_device}", stack_info=True)
                    break
                end = time.perf_counter()
                if interval - (end - start) > 0:
                    time.sleep(interval - (end - start))

        except KeyboardInterrupt:
            self.logger.info("KeyboardInterrupt", exc_info=True)
        finally:
            cap.release()
