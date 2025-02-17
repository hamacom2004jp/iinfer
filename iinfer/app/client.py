from cmdbox.app import client
from cmdbox.app.commons import convert
from pathlib import Path
from iinfer.app import common as cmn
from iinfer.app.commons import module
from typing import List
import base64
import cv2
import datetime
import glob
import logging
import json
import numpy as np
import time


class Client(client.Client):
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
        super().__init__(logger, redis_host, redis_port, redis_password, svname)

    def deploy(self, name:str, model_img_width:int, model_img_height:int, model_file:str, model_conf_file:List[Path], predict_type:str,
               custom_predict_py:Path, label_file:Path, color_file:Path,
               before_injection_conf:Path, before_injection_type:List[str], before_injection_py:List[Path],
               after_injection_conf:Path, after_injection_type:List[str], after_injection_py:List[Path],
               train_dataset:Path, train_dataset_upload:bool, train_type:str, custom_train_py:Path,
               overwrite:bool, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        モデルをRedisサーバーにデプロイする

        Args:
            name (str): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            model_file (str): モデルファイルのパス又はURL
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
            train_dataset (Path): 学習データセットディレクトリのパス
            train_dataset_upload (bool): 学習データセットをサーバーにアップロードするかどうか
            train_type (str): 学習方法のタイプ
            custom_train_py (Path): 学習スクリプトのパス
            overwrite (bool): モデルを上書きするかどうか
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        if " " in name:
            self.logger.warning(f"name contains whitespace.")
            return {"error": f"name contains whitespace."}
        if model_file is None:
            self.logger.warning(f"model_file or model_file is empty.")
            return {"error": f"model_file or model_file is empty."}
        if predict_type is None:
            self.logger.warning(f"predict_type is empty.")
            return {"error": f"predict_type is empty."}
        if predict_type not in cmn.BASE_MODELS and predict_type != "Custom":
            self.logger.warning(f"Unknown predict_type. {predict_type}")
            return {"error": f"Unknown predict_type. {predict_type}"}
        if predict_type == 'Custom':
            if custom_predict_py is None or not custom_predict_py.exists():
                self.logger.warning(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                return {"error": f"custom_predict_py path {str(custom_predict_py)} does not exist"}
            with open(custom_predict_py, "rb") as pf:
                custom_predict_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
            pred = module.load_custom_predict(custom_predict_py, self.logger)
            model_img_width = pred.IMAGE_WIDTH
            model_img_height = pred.IMAGE_HEIGHT
        else:
            custom_predict_py_b64 = None
            if model_img_width is None or model_img_width <= 0:
                model_img_width = cmn.BASE_MODELS[predict_type]['image_width']
            if model_img_height is None or model_img_height <= 0:
                model_img_height = cmn.BASE_MODELS[predict_type]['image_height']
        if before_injection_type is not None and len(before_injection_type) > 0:
            for t in before_injection_type:
                if t not in cmn.BASE_BREFORE_INJECTIONS:
                    self.logger.warning(f"Unknown before_injection_type. {t}")
                    return {"error": f"Unknown before_injection_type. {t}"}
            before_injection_type = ','.join(before_injection_type)
        if after_injection_type is not None and len(after_injection_type) > 0:
            for t in after_injection_type:
                if t not in cmn.BASE_AFTER_INJECTIONS:
                    self.logger.warning(f"Unknown after_injection_type. {t}")
                    return {"error": f"Unknown after_injection_type. {t}"}
            after_injection_type = ','.join(after_injection_type)
        def _conf_b64(name:str, conf:Path):
            if conf is not None and not conf.exists():
                self.logger.warning(f"{name} {conf} does not exist")
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
        if model_file is not None and not model_file.startswith("http://") and not model_file.startswith("https://"):
            model_file = Path(model_file)
            if model_file.exists():
                with open(model_file, "rb") as mf:
                    model_bytes_b64 = base64.b64encode(mf.read()).decode('utf-8')
            elif predict_type != 'Custom' and cmn.BASE_MODELS[predict_type]['required_model_weight']:
                self.logger.warning(f"model_file {model_file} does not exist")
                return {"error": f"model_file {model_file} does not exist"}
            else:
                model_bytes_b64 = None
        else:
            model_bytes_b64 = None
        def _name_b64(aname:str, files:List[Path]):
            if files is not None:
                b64s = []
                names = []
                for p in files:
                    if not p.exists():
                        self.logger.warning(f"{aname} {p} does not exist")
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

        if train_dataset is not None:
            if train_type is None:
                self.logger.warning(f"train_type is empty.Required if train_dataset is specified.")
                return {"error": f"train_type is empty.Required if train_dataset is specified."}
            if not train_dataset.exists():
                self.logger.warning(f"train_dataset path {str(train_dataset)} does not exist")
                return {"error": f"train_dataset path {str(train_dataset)} does not exist"}
            if not train_dataset.is_dir():
                self.logger.warning(f"train_dataset path {str(train_dataset)} does not directory")
                return {"error": f"train_dataset path {str(train_dataset)} does not directory"}
        if train_type is not None and train_dataset is None:
            self.logger.warning(f"train_dataset is empty.Required if train_type is specified.")
            return {"error": f"train_dataset is empty.Required if train_type is specified."}
        if train_type is not None and train_type not in cmn.BASE_TRAIN_MODELS and train_type != "Custom":
            self.logger.warning(f"Unknown train_type. {train_type}")
            return {"error": f"Unknown train_type. {train_type}"}
        if train_type == 'Custom':
            if custom_train_py is None or not custom_train_py.exists():
                self.logger.warning(f"custom_train_py path {str(custom_train_py)} does not exist")
                return {"error": f"custom_train_py path {str(custom_train_py)} does not exist"}
            with open(custom_train_py, "rb") as pf:
                custom_train_py_b64 = base64.b64encode(pf.read()).decode('utf-8')
        else:
            custom_train_py_b64 = None

        res_json = self.redis_cli.send_cmd('deploy', [name, str(model_img_width), str(model_img_height), predict_type,
                                           model_file.name if isinstance(model_file, Path) else model_file, model_bytes_b64,
                                           model_conf_file_name, model_conf_bytes_b64,
                                           custom_predict_py_b64, label_file_b64, color_file_b64,
                                           before_injection_conf_b64, before_injection_type, before_injection_py_name, before_injection_py_b64,
                                           after_injection_conf_b64, after_injection_type, after_injection_py_name, after_injection_py_b64,
                                           'input' if train_dataset is not None and train_dataset_upload else None,
                                           train_type, custom_train_py_b64, overwrite],
                                           retry_count=retry_count, retry_interval=retry_interval, outstatus=False, timeout=timeout)

        if train_dataset is not None and train_dataset_upload:
            data_files = glob.glob(str(train_dataset / "**" / "*"), recursive=True)
            svpath = Path(f"/{name}")
            for f in data_files:
                file_path = Path(f)
                if file_path.is_dir():
                    continue
                p = f.replace(str(train_dataset), '', 1).replace('\\', '/')
                up_path = svpath / 'input' / p[1:] if p.startswith('/') else svpath / p
                rj = self.file_upload(up_path, file_path, scope="server", mkdir=True, orverwrite=True,
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
                if 'success' not in rj:
                    return rj

        return res_json

    def train(self, name:str, overwrite:bool, retry_count:int=3, retry_interval:int=5, timeout:int = 3*3600):
        """
        モデルをRedisサーバーで学習する

        Args:
            name (str): モデル名
            overwrite (bool): モデルを上書きするかどうか
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 3*3600.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        if " " in name:
            self.logger.warning(f"name contains whitespace.")
            return {"error": f"name contains whitespace."}

        res_json = self.redis_cli.send_cmd('train', [name, overwrite],
                                           retry_count=retry_count, retry_interval=retry_interval, outstatus=False, timeout=timeout)
        return res_json

    def deploy_list(self, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        デプロイされたモデルのリストを取得する

        Args:
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self.redis_cli.send_cmd('deploy_list', [],
                                           retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json

    def undeploy(self, name:str, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        モデルをRedisサーバーからアンデプロイする

        Args:
            name (str): モデル名
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        res_json = self.redis_cli.send_cmd('undeploy', [name],
                                           retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json

    def start(self, name:str, model_provider:str = 'CPUExecutionProvider', use_track:bool=False, gpuid:int=None,
              retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        モデルをRedisサーバーで起動する

        Args:
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            use_track (bool): Multi Object Trackerを使用するかどうか, by default False
            gpuid (int): GPU ID, by default None
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        if model_provider is None or model_provider == "":
            self.logger.warning(f"model_provider is empty.")
            return {"error": f"model_provider is empty."}
        res_json = self.redis_cli.send_cmd('start', [name, model_provider, str(use_track), str(gpuid)],
                                           retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json

    def stop(self, name:str,
             retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        モデルをRedisサーバーで停止する

        Args:
            name (str): モデル名
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        res_json = self.redis_cli.send_cmd('stop', [name],
                                           retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json


    def stop_server(self, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        Redisサーバーを停止する

        Args:
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self.redis_cli.send_cmd('stop_server', [], retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json

    def predict(self, name:str, image = None, image_file = None, image_file_enable:bool=True, pred_input_type:str = 'jpeg',
                output_image_file:str = None, output_preview:bool=False, nodraw:bool=False,
                retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            name (str): モデル名
            image (np.ndarray | bytes, optional): 画像データ. Defaults to None. np.ndarray型の場合はデコードしない(RGBであること).
            image_file (str|file-like object, optional): 画像ファイルのパス. Defaults to None.
            image_file_enable (bool, optional): 画像ファイルを使用するかどうか. Defaults to True. image_fileがNoneでなく、このパラメーターがTrueの場合はimage_fileを使用する.
            pred_input_type (str, optional): 画像の形式. Defaults to 'jpeg'.
            output_image_file (str, optional): 予測結果の画像ファイルのパス. Defaults to None.
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
            nodraw (bool, optional): 描画フラグ. Defaults to False.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        spredtime = time.perf_counter()
        if name is None or name == "":
            self.logger.warning(f"name is empty.")
            return {"error": f"name is empty."}
        if image is None and image_file is None:
            self.logger.warning(f"image and image_file is empty.")
            return {"error": f"image and image_file is empty."}
        npy_b64 = None
        simgloadtime = time.perf_counter()
        if image_file is not None and image_file_enable:
            if type(image_file) == str:
                if not Path(image_file).exists():
                    self.logger.warning(f"Not found image_file. {image_file}.")
                    return {"error": f"Not found image_file. {image_file}."}
            if pred_input_type == 'jpeg' or pred_input_type == 'png' or pred_input_type == 'bmp':
                f = None
                try:
                    f = image_file if type(image_file) is not str else open(image_file, "rb")
                    img_npy = convert.imgfile2npy(f)
                finally:
                    if f is not None: f.close()
            elif pred_input_type == 'capture':
                f = None
                try:
                    f = image_file if type(image_file) is not str else open(image_file, "r", encoding='utf-8')
                    res_list = []
                    for line in f:
                        if type(line) is bytes:
                            line = line.decode('utf-8')
                        capture_data = line.strip().split(',')
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
                        res_json = self.predict(name, image=img_npy, image_file=fn, image_file_enable=False,
                                                output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw,
                                                retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"capture file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
                except UnicodeDecodeError as e:
                    self.logger.error(f"capture file or pred_input_type setting is invalid. pred_input_type={pred_input_type}. {e}", exc_info=True)
                    return {"error": f"capture file or pred_input_type setting is invalid. pred_input_type={pred_input_type}. {e}"}
                finally:
                    if f is not None: f.close()
            elif pred_input_type == 'output_json':
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
                        res_json = self.predict(name, image=img_npy, image_file=Path(res_json['output_image_name'].strip()), image_file_enable=False,
                                                output_image_file=output_image_file, output_preview=output_preview, nodraw=nodraw,
                                                retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"output_json file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
                finally:
                    if f is not None: f.close()
            else:
                self.logger.warning(f"pred_input_type is invalid. {pred_input_type}.")
                return {"error": f"pred_input_type is invalid. {pred_input_type}."}
        else:
            if type(image) == np.ndarray:
                img_npy = image
                if image_file is None: image_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.capture'
                image_file_enable = False
            elif pred_input_type == 'capture':
                image = image.decode(encoding="utf-8") if type(image) is bytes else image
                capture_data = image.split(',')
                if len(capture_data) < 6:
                    self.logger.warning(f"capture data is invalid. {image}.")
                    return {"error": f"capture data is invalid. {image}."}
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
            elif pred_input_type == 'output_json':
                res_json = json.loads(image)
                if not ("output_image" in res_json and "output_image_shape" in res_json and "output_image_name" in res_json):
                    self.logger.warning(f"image_file data is invalid. Not found output_image or output_image_shape or output_image_name key.")
                    return {"error": f"image_file data is invalid. Not found output_image or output_image_shape or output_image_name key."}
                if res_json["output_image_name"].endswith(".capture"):
                    img_npy = convert.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
                else:
                    img_bytes = convert.b64str2bytes(res_json["output_image"])
                    img_npy = convert.imgbytes2npy(img_bytes)
                if image_file is None: image_file = res_json["output_image_name"]
                image_file_enable = False
            elif pred_input_type == 'jpeg' or pred_input_type == 'png' or pred_input_type == 'bmp':
                img_npy = convert.imgbytes2npy(image)
                if image_file is None: image_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.{pred_input_type}'
                image_file_enable = False
            else:
                self.logger.warning(f"pred_input_type is invalid. {pred_input_type}.")
                return {"error": f"pred_input_type is invalid. {pred_input_type}."}

        eimgloadtime = time.perf_counter()
        npy_b64 = convert.npy2b64str(img_npy)
        res_json = self.redis_cli.send_cmd('predict',
                                [name, npy_b64, str(nodraw), str(img_npy.shape[0]), str(img_npy.shape[1]),
                                str(img_npy.shape[2] if len(img_npy.shape) > 2 else '-1'), image_file],
                                retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        soutputtime = time.perf_counter()
        if "output_image" in res_json and "output_image_shape" in res_json:
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
                except Exception as e:
                    self.logger.error(f"cv2.imshow error. {e}", exc_info=True)
                    pass
        eoutputtime = time.perf_counter()
        epredtime = time.perf_counter()
        if "success" in res_json:
            if "performance" not in res_json["success"]:
                res_json["success"]["performance"] = []
            performance = res_json["success"]["performance"]
            performance.append(dict(key="cl_imgload", val=f"{eimgloadtime-simgloadtime:.3f}s"))
            performance.append(dict(key="cl_output", val=f"{eoutputtime-soutputtime:.3f}s"))
            performance.append(dict(key="cl_pred", val=f"{epredtime-spredtime:.3f}s"))
        return res_json

    def read_dir(self, glob_str:str, read_input_type:str='jpeg', image_type:str='capture', root_dir:Path=Path('.'), include_hidden=True,
                 moveto:Path=None, polling:bool=False, polling_count:int=10, polling_interval:int=1):
        """
        ディレクトリ内の画像ファイルを取得します

        Args:
            glob_str (str): 読込むファイルのglobパターン
            read_input_type (str, optional): 読み込みタイプ. Defaults to 'jpeg'.
            image_type (str, optional): 画像の形式. Defaults to 'capture'.
            root_dir (Path, optional): 検索の基準となるルートディレクトリ. Defaults to Path('.').
            include_hidden (bool, optional): 隠しファイルを含めるかどうか. Defaults to True.
            moveto (Path, optional): 読み込んだファイルを移動する先のディレクトリ. Defaults to None.
            polling (bool, optional): 定期的にディレクトリ内の読込みを繰り返すかどうか. Defaults to False.
            polling_count (int, optional): ポーリング回数. Defaults to 10.
            polling_interval (int, optional): ポーリング間隔. Defaults to 1.

        Yields:
            Tuple[str, str, int, int, int, str]: 画像の形式, 画像のBase64文字列, 画像の高さ, 画像の幅, 画像の色数, 画像のファイル名
        """
        if root_dir is None or not root_dir.exists():
            self.logger.warning(f"root_dir {root_dir} does not exist.")
            raise FileNotFoundError(f"root_dir {root_dir} does not exist.")
        if polling_interval <= 0:
            self.logger.warning(f"polling_interval {polling_interval} is invalid.")
            raise ValueError(f"polling_interval {polling_interval} is invalid.")
        def _read_file(p:Path, image_type:str):
            img_npy = convert.imgfile2npy(p)
            if image_type == 'capture':
                img_b64 = convert.npy2b64str(img_npy)
            elif image_type != 'capture':
                img_b64 = convert.bytes2b64str(convert.npy2imgfile(img_npy, image_type=image_type))
            return image_type, img_b64, img_npy.shape[0], img_npy.shape[1], img_npy.shape[2] if len(img_npy.shape) > 2 else -1, p.name

        def _read_dir(glob_str:str, read_input_type:str, image_type:str, root_dir:Path, include_hidden:bool, moveto:Path):
            files = glob.glob(glob_str, root_dir=root_dir, include_hidden=include_hidden, recursive=True)
            for file in files:
                p = root_dir / file
                if not p.is_file():
                    continue
                if self.logger.level == logging.DEBUG:
                    self.logger.debug(f"read file: {p}")
                if read_input_type == 'capture':
                    with open(p, 'r', encoding='utf-8') as f:
                        for line in f:
                            cel = line.split(',')
                            if cel[0] != image_type:
                                if cel[0] == 'capture':
                                    img_npy = convert.b64str2npy(cel[1], shape=(int(cel[2]), int(cel[3]), int(cel[4]) if int(cel[4]) > 0 else 1))
                                else:
                                    img_npy = convert.imgbytes2npy(convert.b64str2bytes(cel[1]))
                                cel[0] = image_type
                                cel[1] = convert.npy2b64str(img_npy)
                            yield cel[0], cel[1], cel[2], cel[3], cel[4], cel[5]
                elif read_input_type == 'filelist':
                    with open(p, 'r', encoding='utf-8') as f:
                        for line in f:
                            p = Path(line)
                            cel = _read_file(p, image_type)
                            yield cel[0], cel[1], cel[2], cel[3], cel[4], cel[5]
                else:
                    cel = _read_file(p, image_type)
                    yield cel[0], cel[1], cel[2], cel[3], cel[4], cel[5]
                if moveto is not None:
                    mv = moveto / file
                    if self.logger.level == logging.DEBUG:
                        self.logger.debug(f"move file: {p} => {mv}")
                    mv.parent.mkdir(parents=True, exist_ok=True)
                    p.rename(mv)
        
        if polling:
            count = 0
            while True:
                for cel in _read_dir(glob_str, read_input_type, image_type, root_dir, include_hidden, moveto):
                    yield cel
                count += 1
                if count >= polling_count and polling_count > 0:
                    break
                time.sleep(polling_interval)
        else:
            for cel in _read_dir(glob_str, read_input_type, image_type, root_dir, include_hidden, moveto):
                yield cel

    def capture(self, capture_device='0', image_type:str='capture', capture_frame_width:int=None, capture_frame_height:int=None,
                capture_fps:int=1000, output_preview:bool=False):
        """
        ビデオをキャプチャしてその結果を出力する

        Args:
            capture_device (int or str): キャプチャするディバイス、ビデオデバイスのID, ビデオファイルのパス。rtspのURL. by default 0
            image_type (str, optional): 画像の形式. Defaults to 'capture'.
            capture_frame_width (int): キャプチャするビデオのフレーム幅, by default None
            capture_frame_height (int): キャプチャするビデオのフレーム高さ, by default None
            capture_fps (int): キャプチャするビデオのフレームレート, by default 1000
            output_preview (bool, optional): 予測結果の画像をプレビューするかどうか. Defaults to False.
        """
        if capture_device.isdecimal():
            capture_device = int(capture_device)
        cap = cv2.VideoCapture(capture_device)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        cap.set(cv2.CAP_PROP_FPS, 30)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('H', '2', '6', '4'))
        if capture_frame_width is not None:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, capture_frame_width)
        if capture_frame_height is not None:
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, capture_frame_height)
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
                    self.logger.warning(f"Capture failed. devide_id={capture_device}", stack_info=True)
                    break
                end = time.perf_counter()
                if interval - (end - start) > 0:
                    time.sleep(interval - (end - start))

        except KeyboardInterrupt:
            self.logger.warning("KeyboardInterrupt", exc_info=True)
        finally:
            cap.release()
