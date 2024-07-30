from motpy import Detection, MultiObjectTracker
from pathlib import Path
from PIL import Image
from iinfer.app import common, filer, predict, injection
from iinfer.app.commons import convert, module, redis_client
from typing import List, Dict, Any, Tuple, Union
import base64
import datetime
import logging
import json
import os
import threading
import numpy as np
import redis
import shutil
import time
import urllib


class Server(filer.Filer):

    def __init__(self, data_dir: Path, logger: logging.Logger, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None, svname: str = 'server'):
        """
        Redisサーバーに接続し、クライアントからのコマンドを受信し実行する

        Args:
            data_dir (Path): データフォルダのパス
            logger (logging): ロガー
            redis_host (str): Redisホスト名, by default "localhost"
            redis_port (int): Redisポート番号, by default 6379
            redis_password (str): Redisパスワード, by default None
            svname (str, optional): 推論サーバーのサービス名. by default 'server'
        """
        super().__init__(data_dir, logger)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = svname
        self.redis_cli = None
        self.sessions:Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.train_thread = None

    def __enter__(self):
        self.start_server()
        return self

    def __exit__(self, a, b, c):
        self.terminate_server()

    def start_server(self, retry_count:int=20, retry_interval:int=5):
        """
        サーバー処理を開始する
        """
        self.is_running = False
        self.redis_cli = redis_client.RedisClient(self.logger, host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname)
        if self.redis_cli.check_server(find_svname=False, retry_count=retry_count, retry_interval=retry_interval, outstatus=True):
            self.is_running = True
            self._run_server()

    def list_server(self):
        """
        起動しているサーバーリストを取得する

        Returns:
            List[str]: サーバーのリスト
        """
        self.redis_cli = redis_client.RedisClient(self.logger, host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname)
        hblist = self.redis_cli.keys("hb-*")
        svlist = []
        for hb in hblist:
            svname = hb.decode().replace("hb-", "")
            recive_cnt = -1
            sccess_cnt = -1
            warn_cnt = -1
            error_cnt = -1
            try:
                if self.redis_cli.hexists(hb, 'recive_cnt'):
                    val = self.redis_cli.hget(hb, 'recive_cnt')
                    recive_cnt = int(val.decode()) if val is not None else -1
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    val = self.redis_cli.hget(hb, 'sccess_cnt')
                    sccess_cnt = int(val.decode()) if val is not None else -1
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    val = self.redis_cli.hget(hb, 'warn_cnt')
                    warn_cnt = int(val.decode()) if val is not None else -1
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    val = self.redis_cli.hget(hb, 'error_cnt')
                    error_cnt = int(val.decode()) if val is not None else -1
            except redis.exceptions.ResponseError:
                self.logger.warn(f"Failed to get ctime. {hb}", exc_info=True)
            svlist.append(dict(svname=svname, recive_cnt=recive_cnt, sccess_cnt=sccess_cnt, warn_cnt=warn_cnt, error_cnt=error_cnt))
        if len(svlist) <= 0:
            return {"warn": "No server is running."}
        return {"success": svlist}

    def _clean_server(self):
        """
        Redisサーバーに残っている停止済みのサーバーキーを削除する
        """
        hblist = self.redis_cli.keys("hb-*")
        for hb in hblist:
            try:
                v = self.redis_cli.hget(hb, 'ctime')
                if v is None:
                    continue
            except redis.exceptions.ResponseError:
                self.logger.warn(f"Failed to get ctime. {hb}", exc_info=True)
                continue
            tm = float(v)
            if time.time() - tm > 10:
                self.redis_cli.delete(hb)
                self.redis_cli.delete(hb.decode().replace("hb-", "sv-"))

    def _run_server(self):
        self.logger.info(f"start server. svname={self.svname}")
        ltime = time.time()
        recive_cnt = 0
        sccess_cnt = 0
        warn_cnt = 0
        error_cnt = 0
        self.redis_cli.hset(self.redis_cli.hbname, 'recive_cnt', recive_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'sccess_cnt', sccess_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'warn_cnt', warn_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'error_cnt', error_cnt)
        while self.is_running:
            try:
                # ブロッキングリストから要素を取り出す
                ctime = time.time()
                self.redis_cli.hset(self.redis_cli.hbname, 'ctime', ctime)
                result = self.redis_cli.blpop(self.redis_cli.svname)
                if ctime - ltime > 10:
                    self._clean_server()
                    ltime = ctime
                if result is None or len(result) <= 0:
                    time.sleep(1)
                    continue
                msg = result[1].decode().split(' ')
                if len(msg) <= 0:
                    time.sleep(1)
                    continue
                st = None
                recive_cnt += 1
                self.redis_cli.hset(self.redis_cli.hbname, 'recive_cnt', recive_cnt)

                if msg[0] == 'deploy':
                    if msg[7] == 'None':
                        model_bin = None
                    else:
                        model_bin = base64.b64decode(msg[7])
                    if msg[8] == 'None':
                        model_conf_file = None
                    else:
                        model_conf_file = msg[8].split(',')
                    if msg[9] == 'None':
                        model_conf_bin = None
                    else:
                        model_conf_bin = [base64.b64decode(m) for m in msg[9].split(',')]
                    if msg[10] == 'None':
                        custom_predict_py = None
                    else:
                        custom_predict_py = base64.b64decode(msg[10])
                    if msg[11] == 'None':
                        label_txt = None
                    else:
                        label_txt = base64.b64decode(msg[11])
                    if msg[12] == 'None':
                        color_txt = None
                    else:
                        color_txt = base64.b64decode(msg[12])
                    if msg[13] == 'None':
                        before_injection_conf = None
                    else:
                        before_injection_conf = base64.b64decode(msg[13])
                    if msg[14] == 'None':
                        before_injection_type = None
                    else:
                        before_injection_type = msg[14].split(',')
                    if msg[15] == 'None':
                        before_injection_py = None
                    else:
                        before_injection_py = msg[15].split(',')
                    if msg[16] == 'None':
                        before_injection_bin = None
                    else:
                        before_injection_bin = [base64.b64decode(m) for m in msg[16].split(',')]
                    if msg[17] == 'None':
                        after_injection_conf = None
                    else:
                        after_injection_conf = base64.b64decode(msg[17])
                    if msg[18] == 'None':
                        after_injection_type = None
                    else:
                        after_injection_type = msg[18].split(',')
                    if msg[19] == 'None':
                        after_injection_py = None
                    else:
                        after_injection_py = msg[19].split(',')
                    if msg[20] == 'None':
                        after_injection_bin = None
                    else:
                        after_injection_bin = [base64.b64decode(m) for m in msg[20].split(',')]
                    if msg[21] == 'True':
                        overwrite = True
                    else:
                        overwrite = False

                    st = self.deploy(msg[1], msg[2], int(msg[3]), int(msg[4]), msg[5], msg[6],
                                     model_bin, model_conf_file, model_conf_bin, custom_predict_py, label_txt, color_txt,
                                     before_injection_conf, before_injection_type, before_injection_py, before_injection_bin,
                                     after_injection_conf, after_injection_type, after_injection_py, after_injection_bin, overwrite)

                elif msg[0] == 'train':
                    if msg[4] == 'None':
                        model_conf_file = None
                    else:
                        model_conf_file = msg[4].split(',')
                    if msg[5] == 'None':
                        model_conf_bin = None
                    else:
                        model_conf_bin = [base64.b64decode(m) for m in msg[5].split(',')]
                    if msg[6] == 'None':
                        custom_train_py = None
                    else:
                        custom_train_py = base64.b64decode(msg[6])
                    if msg[7] == 'True':
                        overwrite = True
                    else:
                        overwrite = False
                    st = self.train(msg[1], msg[2], msg[3], model_conf_file, model_conf_bin, custom_train_py, overwrite)

                elif msg[0] == 'deploy_list':
                    st = self.deploy_list(msg[1])
                elif msg[0] == 'undeploy':
                    st = self.undeploy(msg[1], msg[2])
                elif msg[0] == 'start':
                    st = self.start(msg[1], msg[2], msg[3], (True if msg[4]=='True' else False), (None if msg[5]=='None' else msg[5]))
                elif msg[0] == 'stop':
                    st = self.stop(msg[1], msg[2])
                elif msg[0] == 'predict':
                    nodraw = True if msg[4] == 'True' else False
                    shape = [int(msg[5]), int(msg[6])]
                    if int(msg[7]) > 0: shape.append(int(msg[7]))
                    output_image_name = msg[8]
                    if shape[0] >0 and shape[1] > 0:
                        img_npy = convert.b64str2npy(msg[3], shape)
                        image = convert.npy2img(img_npy)
                        st = self.predict(msg[1], msg[2], image, output_image_name, nodraw)
                    else:
                        st = self.predict(msg[1], msg[2], convert.b64str2str(msg[3]), output_image_name, nodraw)
                elif msg[0] == 'stop_server':
                    self.is_running = False
                    self.redis_cli.rpush(msg[1], {"success": f"Successful stop server. svname={self.redis_cli.svname}"})
                    break
                elif msg[0] == 'file_list':
                    svpath = convert.b64str2str(msg[2])
                    st = self.file_list(msg[1], svpath)
                elif msg[0] == 'file_mkdir':
                    svpath = convert.b64str2str(msg[2])
                    st = self.file_mkdir(msg[1], svpath)
                elif msg[0] == 'file_rmdir':
                    svpath = convert.b64str2str(msg[2])
                    st = self.file_rmdir(msg[1], svpath)
                elif msg[0] == 'file_download':
                    svpath = convert.b64str2str(msg[2])
                    st = self.file_download(msg[1], svpath)
                elif msg[0] == 'file_upload':
                    svpath = convert.b64str2str(msg[2])
                    file_name = convert.b64str2str(msg[3])
                    file_data = convert.b64str2bytes(msg[4])
                    mkdir = msg[5]=='True'
                    orverwrite = msg[6]=='True'
                    st = self.file_upload(msg[1], svpath, file_name, file_data, mkdir, orverwrite)
                elif msg[0] == 'file_remove':
                    svpath = convert.b64str2str(msg[2])
                    st = self.file_remove(msg[1], svpath)
                else:
                    self.logger.warn(f"Unknown command {msg}")
                    st = self.RESP_WARN

                if st==self.RESP_SCCESS:
                    sccess_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'sccess_cnt', sccess_cnt)
                elif st==self.RESP_WARN:
                    warn_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'warn_cnt', warn_cnt)
                elif st==self.RESP_ERROR:
                    error_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'error_cnt', error_cnt)
            except redis.exceptions.TimeoutError:
                pass
            except redis.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection to the server was lost. {e}")
                self.is_running = False
                break
            except KeyboardInterrupt as e:
                self.is_running = False
                break
            except Exception as e:
                self.logger.warning(f"Unknown error occurred. {e}", exc_info=True)
                self.is_running = False
                break
        self.redis_cli.delete(self.redis_cli.svname)
        self.redis_cli.delete(self.redis_cli.hbname)
        self.logger.info(f"stop server. svname={self.redis_cli.svname}")

    def terminate_server(self):
        """
        サーバー処理を終了する
        """
        self.redis_cli.close()
        self.logger.info(f"terminate server.")

    def deploy(self, reskey:str, name:str, model_img_width:int, model_img_height:int, predict_type:str,
               model_file:str, model_bin:bytes, model_conf_file:List[str], model_conf_bin:List[bytes],
               custom_predict_py:bytes, label_txt:bytes, color_txt:bytes,
               before_injection_conf:bytes, before_injection_type:List[str], before_injection_py:List[str], before_injection_bin:List[bytes],
               after_injection_conf:bytes, after_injection_type:List[str], after_injection_py:List[str], after_injection_bin:List[bytes], overwrite:bool):
        """
        モデルをデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            model_img_width (int): 画像の幅
            model_img_height (int): 画像の高さ
            predict_type (str): 推論方法のタイプ
            model_file (str): モデルのファイル名
            model_bin (bytes): モデルファイル
            model_conf_file (List[str]): モデル設定のファイル名
            model_conf_bin (List[bytes]): モデル設定ファイル
            custom_predict_py (bytes): 推論のPythonスクリプト
            label_txt (bytes): ラベルファイル
            color_txt (bytes): 色設定ファイル
            before_injection_conf (bytes): 推論前処理の設定ファイル
            before_injection_type (List[str]): 推論前処理のタイプ
            before_injection_py (List[str]): 推論前処理のPythonスクリプトファイル名
            before_injection_bin (List[bytes]): 推論前処理のPythonスクリプト
            after_injection_conf (bytes): 推論後処理の設定ファイル
            after_injection_type (List[str]): 推論後処理のタイプ
            after_injection_py (List[str]): 推論後処理のPythonスクリプトファイル名
            after_injection_bin (List[bytes]): 推論後処理のPythonスクリプト
            overwrite (bool): 上書きするかどうか
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if model_file is None or model_file == "":
            self.logger.warn(f"model_file is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"model_file is empty."})
            return self.RESP_WARN
        if model_img_width is None or model_img_width <= 0:
            self.logger.warn(f"Image width is invalid.")
            self.redis_cli.rpush(reskey, {"warn": f"Image width is invalid."})
            return self.RESP_WARN
        if model_img_height is None or model_img_height <= 0:
            self.logger.warn(f"Image height is invalid.")
            self.redis_cli.rpush(reskey, {"warn": f"Image height is invalid."})
            return self.RESP_WARN

        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        if not overwrite and deploy_dir.exists():
            self.logger.warn(f"Could not be deployed. '{deploy_dir}' already exists")
            self.redis_cli.rpush(reskey, {"warn": f"Could not be deployed. '{deploy_dir}' already exists"})
            return self.RESP_WARN

        if predict_type != "Custom":
            if predict_type not in common.BASE_MODELS:
                self.logger.warn(f"Incorrect predict_type. '{predict_type}'")
                self.redis_cli.rpush(reskey, {"warn": f"Incorrect predict_type. '{predict_type}'"})
                return self.RESP_WARN
            if common.BASE_MODELS[predict_type]['required_model_conf']==True and model_conf_file is None:
                self.logger.warn(f"model_conf_file is None.")
                self.redis_cli.rpush(reskey, {"warn": f"model_conf_file is None."})
                return self.RESP_WARN

        common.mkdirs(deploy_dir)
        def _save_s(file:str, data:bytes, ret_fn:bool=False):
            if file is None or data is None:
                return False, None
            file = deploy_dir / file
            with open(file, "wb") as f:
                f.write(data)
                self.logger.info(f"Save {file} to {str(deploy_dir)}")
            return True, file if ret_fn else None

        if model_file.startswith("http") and (model_bin is None or model_bin == ''):
            model_path = deploy_dir / urllib.parse.urlparse(model_file).path.split('/')[-1]
            if not model_path.exists():
                self.logger.info(f"Downloading. {model_file}")
                urllib.request.urlretrieve(model_file, model_path)
                self.logger.info(f"Save {model_path}")
            else:
                self.logger.info(f"Already exists. {model_path}")
            model_file = model_path
        else:
            ret, model_file = _save_s(model_file, model_bin, ret_fn=True)

        ret, before_injection_conf = _save_s("before_injection_conf.json", before_injection_conf, ret_fn=True)
        ret, after_injection_conf = _save_s("after_injection_conf.json", after_injection_conf, ret_fn=True)

        def _save_m(name:str, files:List[str], datas:List[bytes]):
            if files is not None and datas is None:
                self.logger.warn(f"{name}_file is not None but {name}_bin is None.")
                self.redis_cli.rpush(reskey, {"warn": f"{name}_file is not None but {name}_bin is None."})
                return False, files
            if files is None and datas is not None:
                self.logger.warn(f"{name}_file is None but {name}_bin is not None.")
                self.redis_cli.rpush(reskey, {"warn": f"{name}_file is None but {name}_bin is not None."})
                return False, files
            if files is not None:
                files = [deploy_dir / cf for cf in files if cf is not None and cf != '']
                for i, cf in enumerate(files):
                    with open(cf, "wb") as f:
                        f.write(datas[i])
                        self.logger.info(f"Save {cf} to {str(deploy_dir)}")
            return True, files
        ret, model_conf_file = _save_m('model_conf', model_conf_file, model_conf_bin)
        if not ret: return self.RESP_WARN
        ret, before_injection_py = _save_m('before_injection', before_injection_py, before_injection_bin)
        if not ret: return self.RESP_WARN
        ret, after_injection_py = _save_m('after_injection', after_injection_py, after_injection_bin)
        if not ret: return self.RESP_WARN
        custom_predict_file = None
        if custom_predict_py is not None:
            custom_predict_file = deploy_dir / "custom_predict.py"
            with open(custom_predict_file, "wb") as f:
                f.write(custom_predict_py)
                self.logger.info(f"Save custom_predict.py to {str(deploy_dir)}")
        if label_txt is not None:
            label_file = deploy_dir / 'label.txt'
            with open(label_file, "wb") as f:
                f.write(label_txt)
                self.logger.info(f"Save {label_file} to {str(deploy_dir)}")
        else:
            label_file = None
        if color_txt is not None:
            color_file = deploy_dir / 'color.txt'
            with open(color_file, "wb") as f:
                f.write(color_txt)
                self.logger.info(f"Save {color_file} to {str(deploy_dir)}")
        else:
            color_file = None
        with open(deploy_dir / "conf.json", "w") as f:
            conf = dict(model_img_width=model_img_width, model_img_height=model_img_height, predict_type=predict_type,
                        model_file=model_file, model_conf_file=model_conf_file, custom_predict_py=(custom_predict_file if custom_predict_file is not None else None),
                        label_file=label_file, color_file=color_file, before_injection_conf=before_injection_conf, after_injection_conf=after_injection_conf,
                        before_injection_type=before_injection_type, after_injection_type=after_injection_type,
                        before_injection_py=before_injection_py, after_injection_py=after_injection_py)
            json.dump(conf, f, default=common.default_json_enc)
            self.logger.info(f"Save conf.json to {str(deploy_dir)}")

        self._gitpull(reskey, deploy_dir, predict_type)

        try:
            ret, predict_obj = module.build_predict(conf["predict_type"], conf["custom_predict_py"], self.logger)
            if not ret:
                self.redis_cli.rpush(reskey, predict_obj)
                return self.RESP_WARN
            predict_obj.post_deploy(deploy_dir, conf)
        except Exception as e:
            self.logger.warn(f"Failed to load Predict: {e}", exc_info=True)
            self.redis_cli.rpush(reskey, {"warn": f"Failed to load Predict: {e}"})
            return self.RESP_WARN

        self.redis_cli.rpush(reskey, {"success": f"Save conf.json to {str(deploy_dir)}"})
        return self.RESP_SCCESS

    def _gitpull(self, reskey:str, deploy_dir:Path, predict_type:str):
        if predict_type.startswith('mmpretrain_'):
            if not (self.data_dir / "mmpretrain").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone https://github.com/open-mmlab/mmpretrain.git', logger=self.logger)
                if returncode != 0:
                    self.logger.warning(f"Failed to git clone mmpretrain.")
                    self.redis_cli.rpush(reskey, {"error": f"Failed to git clone mmpretrain."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmpretrain" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmpretrain configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmdet_'):
            if not (self.data_dir / "mmdetection").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone https://github.com/open-mmlab/mmdetection.git', logger=self.logger)
                if returncode != 0:
                    self.logger.warning(f"Failed to git clone mmdetection.")
                    self.redis_cli.rpush(reskey, {"error": f"Failed to git clone mmdetection."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmdetection" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmdetection configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmseg_'):
            if not (self.data_dir / "mmsegmentation").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=self.logger)
                if returncode != 0:
                    self.logger.warning(f"Failed to git clone mmsegmentation.")
                    self.redis_cli.rpush(reskey, {"error": f"Failed to git clone mmsegmentation."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmsegmentation" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmsegmentation configs to {str(deploy_dir / 'configs')}")

    def train(self, reskey:str, name:str, train_type:str,
              model_conf_file:List[str], model_conf_bin:List[bytes],
              custom_train_py:bytes, overwrite:bool):
        """
        モデルをデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            train_type (str): 学習方法のタイプ
            model_conf_file (List[str]): モデル設定のファイル名
            model_conf_bin (List[bytes]): モデル設定ファイル
            custom_train_py (bytes): 学習のPythonスクリプト
            overwrite (bool): 上書きするかどうか
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN

        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        if not overwrite and deploy_dir.exists():
            self.logger.warn(f"Could not be deployed. '{deploy_dir}' already exists")
            self.redis_cli.rpush(reskey, {"warn": f"Could not be deployed. '{deploy_dir}' already exists"})
            return self.RESP_WARN
        if model_conf_file is None or len(model_conf_file) <= 0:
            self.logger.warning(f"model_conf_file path {str(model_conf_file)} is None")
            return {"error": f"model_conf_file path {str(model_conf_file)} is None"}

        if train_type != "Custom":
            if train_type not in common.BASE_TRAIN_MODELS:
                self.logger.warn(f"Incorrect train_type. '{train_type}'")
                self.redis_cli.rpush(reskey, {"warn": f"Incorrect train_type. '{train_type}'"})
                return self.RESP_WARN

        common.mkdirs(deploy_dir)
        def _save_s(file:str, data:bytes, ret_fn:bool=False):
            if file is None or data is None:
                return False, None
            file = deploy_dir / file
            with open(file, "wb") as f:
                f.write(data)
                self.logger.info(f"Save {file} to {str(deploy_dir)}")
            return True, file if ret_fn else None

        def _save_m(name:str, files:List[str], datas:List[bytes]):
            if files is not None and datas is None:
                self.logger.warn(f"{name}_file is not None but {name}_bin is None.")
                self.redis_cli.rpush(reskey, {"warn": f"{name}_file is not None but {name}_bin is None."})
                return False, files
            if files is None and datas is not None:
                self.logger.warn(f"{name}_file is None but {name}_bin is not None.")
                self.redis_cli.rpush(reskey, {"warn": f"{name}_file is None but {name}_bin is not None."})
                return False, files
            if files is not None:
                files = [deploy_dir / cf for cf in files if cf is not None and cf != '']
                for i, cf in enumerate(files):
                    with open(cf, "wb") as f:
                        f.write(datas[i])
                        self.logger.info(f"Save {cf} to {str(deploy_dir)}")
            return True, files
        ret, model_conf_file = _save_m('model_conf', model_conf_file, model_conf_bin)
        if not ret: return self.RESP_WARN

        custom_train_file = None
        if custom_train_py is not None:
            custom_train_file = deploy_dir / "custom_train.py"
            with open(custom_train_file, "wb") as f:
                f.write(custom_train_py)
                self.logger.info(f"Save custom_train.py to {str(deploy_dir)}")

        with open(deploy_dir / "train_conf.json", "w") as f:
            conf = dict(model_img_width=224, model_img_height=224, train_type=train_type,
                        model_conf_file=model_conf_file, custom_train_py=(custom_train_file if custom_train_file is not None else None))
            json.dump(conf, f, default=common.default_json_enc)
            self.logger.info(f"Save train_conf.json to {str(deploy_dir)}")

        self._gitpull(reskey, deploy_dir, train_type)
        train_obj = None
        try:
            ret, train_obj = module.build_train(conf["train_type"], conf["custom_train_py"], self.logger)
            if not ret:
                self.redis_cli.rpush(reskey, train_obj)
                return self.RESP_WARN
        except Exception as e:
            self.logger.warn(f"Failed to load Train: {e}", exc_info=True)
            self.redis_cli.rpush(reskey, {"warn": f"Failed to load Train: {e}"})
            return self.RESP_WARN

        def _train(train_obj, deploy_dir, model_conf_file, conf, logger):
            cwd = os.getcwd()
            try:
                c = model_conf_file[0] if type(model_conf_file) is list and len(model_conf_file)>0 else str(model_conf_file)
                os.chdir(deploy_dir)
                train_obj.train(deploy_dir, c, train_cfg_options=None)
                train_obj.post_train(deploy_dir, conf)
            except Exception as e:
                logger.warn(f"Failed Train: {e}", exc_info=True)
            finally:
                os.chdir(cwd)

        if self.train_thread is not None and self.train_thread.is_alive():
            self.logger.warn(f"Training is already running.")
            self.redis_cli.rpush(reskey, {"warn": f"Training is already running."})
            return self.RESP_WARN
        self.train_thread = threading.Thread(target=_train, args=(train_obj, deploy_dir, model_conf_file, conf, self.logger))
        self.train_thread.start()

        self.redis_cli.rpush(reskey, {"success": f"Save train_conf.json to {str(deploy_dir)}. Training started. see iinfer_server.log."})
        return self.RESP_SCCESS

    def deploy_list(self, reskey:str):
        """
        デプロイされたモデルのリストを取得する

        Args:
            reskey (str): レスポンスキー

        Returns:
            dict: デプロイされたモデルのリスト
        """
        deploy_list = []
        common.mkdirs(self.data_dir)
        for dir in self.data_dir.iterdir():
            if not dir.is_dir():
                continue
            conf_path = dir / "conf.json"
            if not conf_path.exists():
                self.logger.warn(f"Conf path {str(conf_path)} does not exist")
                continue
            with open(conf_path, "r") as cf:
                conf = json.load(cf)
                model_file = Path(conf["model_file"])
                model_conf_file = None
                if "model_conf_file" in conf and conf["model_conf_file"] is not None and len(conf["model_conf_file"]) > 0 and Path(conf["model_conf_file"][0]).exists():
                    model_conf_file = 'exists'
                before_injection = None
                if "before_injection_py" in conf and conf["before_injection_py"] is not None and len(conf["before_injection_py"]) > 0:
                    if len([True for p in conf["before_injection_py"] if  Path(p).exists()]) > 0:
                        before_injection = 'exists'
                if "before_injection_type" in conf and conf["before_injection_type"] is not None and len(conf["before_injection_type"]) > 0:
                    before_injection = 'enabled'
                after_injection = None
                if "after_injection_py" in conf and conf["after_injection_py"] is not None and len(conf["after_injection_py"]) > 0:
                    if len([True for p in conf["after_injection_py"] if  Path(p).exists()]) > 0:
                        after_injection = 'exists'
                if "after_injection_type" in conf and conf["after_injection_type"] is not None and len(conf["after_injection_type"]) > 0:
                    after_injection = 'enabled'
                custom_predict_py = 'exists' if "custom_predict_py" in conf and conf["custom_predict_py"] is not None and Path(conf["custom_predict_py"]).exists() else None
                label_file = 'exists' if "label_file" in conf and conf["label_file"] is not None and Path(conf["label_file"]).exists() else None
                color_file = 'exists' if "color_file" in conf and conf["color_file"] is not None and Path(conf["color_file"]).exists() else None
                row = dict(name=dir.name,
                           input=(conf["model_img_width"], conf["model_img_height"]), model_file=model_file.name, model_conf_file=model_conf_file,
                           predict_type=conf["predict_type"], custom_predict=custom_predict_py,
                           label_file=label_file, color_file=color_file,
                           session=dir.name in self.sessions,
                           mot=dir.name in self.sessions and self.sessions[dir.name]['tracker'] is not None,
                           before_injection_py=before_injection,
                           after_injection_py=after_injection)
                deploy_list.append(row)
        self.redis_cli.rpush(reskey, {"success": deploy_list})
        return self.RESP_SCCESS

    def undeploy(self, reskey:str, name:str):
        """
        モデルをアンデプロイする

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        deploy_dir = self.data_dir / name
        if not deploy_dir.exists():
            self.logger.warn(f"{name} is not deployed.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} is not deployed."})
            return self.RESP_WARN
        common.rmdirs(deploy_dir)
        self.redis_cli.rpush(reskey, {"success": f"Undeployed {name}. {str(deploy_dir)}"})
        return self.RESP_SCCESS

    def start(self, reskey:str, name:str, model_provider:str, use_track:bool, gpuid:str):
        """
        モデルを読み込み、処理が実行できるようにする

        Args:
            reskey (str): レスポンスキー
            name (str): モデル名
            model_provider (str, optional): 推論実行時のモデルプロバイダー。デフォルトは'CPUExecutionProvider'。
            use_track (bool): Multi Object Trackerを使用するかどうか, by default False
            gpuid (int): GPU ID, by default None
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        conf_path = deploy_dir / "conf.json"
        if not conf_path.exists():
            self.logger.warn(f"Conf path {str(conf_path)} does not exist")
            self.redis_cli.rpush(reskey, {"warn": f"Conf path {str(conf_path)} does not exist"})
            return self.RESP_WARN
        with open(conf_path, "r") as cf:
            conf = json.load(cf)
            if conf['predict_type'] != 'Custom' and common.BASE_MODELS[conf['predict_type']]['required_model_weight']:
                model_path = Path(conf["model_file"])
            else:
                model_path = conf["model_file"]
            if "model_conf_file" in conf and conf["model_conf_file"] is not None and len(conf["model_conf_file"]) > 0:
                model_conf_path = Path(conf["model_conf_file"][0])
            else:
                model_conf_path = None
            try:
                if "before_injection_conf" in conf and conf["before_injection_conf"] is not None:
                    before_injection_conf = dict()
                    with open(conf["before_injection_conf"], "r") as f:
                        before_injection_conf = json.load(f)
                else:
                    before_injection_conf = dict()
                if "before_injection_type" in conf and conf["before_injection_type"] is not None and len(conf["before_injection_type"]) > 0:
                    types = [t for t in conf["before_injection_type"]]
                    before_injections = module.load_before_injection_type(types, before_injection_conf, self.logger)
                else:
                    before_injections = None
                if "before_injection_py" in conf and conf["before_injection_py"] is not None and len(conf["before_injection_py"]) > 0:
                    paths = [Path(p) for p in conf["before_injection_py"]]
                    before_injections = [] if before_injections is None else before_injections
                    before_injections = module.load_before_injections(paths, before_injection_conf, self.logger)
            except Exception as e:
                self.logger.warn(f"Failed to load before_injection: {e}", exc_info=True)
                self.redis_cli.rpush(reskey, {"warn": f"Failed to load before_injection: {e}"})
                return self.RESP_WARN
            try:
                if "after_injection_conf" in conf and conf["after_injection_conf"] is not None:
                    after_injection_conf = dict()
                    with open(conf["after_injection_conf"], "r") as f:
                        after_injection_conf = json.load(f)
                else:
                    after_injection_conf = dict()
                if "after_injection_type" in conf and conf["after_injection_type"] is not None and len(conf["after_injection_type"]) > 0:
                    types = [t for t in conf["after_injection_type"]]
                    after_injections = module.load_after_injection_type(types, after_injection_conf, self.logger)
                else:
                    after_injections = None
                if "after_injection_py" in conf and conf["after_injection_py"] is not None and len(conf["after_injection_py"]) > 0:
                    paths = [Path(p) for p in conf["after_injection_py"]]
                    after_injections = [] if after_injections is None else after_injections
                    after_injections = module.load_after_injections(paths, after_injection_conf, self.logger)
                if type(model_path) is Path and not model_path.exists():
                    self.logger.warn(f"Model path {str(model_path)} does not exist")
                    self.redis_cli.rpush(reskey, {"warn": f"Model path {str(model_path)} does not exist"})
                    return self.RESP_WARN
            except Exception as e:
                self.logger.warn(f"Failed to load after_injection: {e}", exc_info=True)
                self.redis_cli.rpush(reskey, {"warn": f"Failed to load after_injection: {e}"})
                return self.RESP_WARN
            try:
                conf["custom_predict_py"] = conf["custom_predict_py"] if "custom_predict_py" in conf else None
                ret, predict_obj = module.build_predict(conf["predict_type"], conf["custom_predict_py"], self.logger)
                if not ret:
                    self.redis_cli.rpush(reskey, predict_obj)
                    return self.RESP_WARN
            except Exception as e:
                self.logger.warn(f"Failed to load Predict: {e}", exc_info=True)
                self.redis_cli.rpush(reskey, {"warn": f"Failed to load Predict: {e}"})
                return self.RESP_WARN
            if "label_file" in conf and conf["label_file"] is not None:
                label_file = Path(conf["label_file"])
                if not label_file.exists():
                    self.logger.warn(f"label_file path {str(label_file)} does not exist")
                    self.redis_cli.rpush(reskey, {"warn": f"label_file path {str(label_file)} does not exist"})
                    return self.RESP_WARN
                with open(label_file, "r") as f:
                    labels = f.read().splitlines()
            else:
                labels = None
            if "color_file" in conf and conf["color_file"] is not None:
                color_file = Path(conf["color_file"])
                if not color_file.exists():
                    self.logger.warn(f"color_file path {str(color_file)} does not exist")
                    self.redis_cli.rpush(reskey, {"warn": f"color_file path {str(color_file)} does not exist"})
                    return self.RESP_WARN
                with open(color_file, "r") as f:
                    colors = f.read().splitlines()
            else:
                colors = None
            try:
                session = predict_obj.create_session(deploy_dir, model_path, model_conf_path, model_provider, gpu_id=gpuid)
                self.sessions[name] = dict(
                    session=session,
                    model_img_width=conf["model_img_width"],
                    model_img_height=conf["model_img_height"],
                    predict_obj=predict_obj,
                    labels=labels,
                    colors=colors,
                    tracker=MultiObjectTracker(dt=0.1) if use_track else None,
                    before_injections=before_injections,
                    after_injections=after_injections
                )
            except Exception as e:
                self.logger.warn(f"Failed to create session: {e}", exc_info=True)
                self.redis_cli.rpush(reskey, {"warn": f"Failed to create session: {e}"})
                return self.RESP_WARN
        self.logger.info(f"Successful start of {name} session.")
        self.redis_cli.rpush(reskey, {"success": f"Successful start of {name} session."})
        return self.RESP_SCCESS
    
    def stop(self, reskey:str, name:str):
        """
        モデルを開放する

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has not yet started a session."})
            return self.RESP_WARN
        #self.sessions[name]['session'].close()
        del self.sessions[name]
        self.logger.info(f"Successful stop of {name} session.")
        self.redis_cli.rpush(reskey, {"success": f"Successful stop of {name} session."})
        return self.RESP_SCCESS

    def predict(self, reskey:str, name:str, input_data:Union[Image.Image, str], output_image_name:str, nodraw:bool):
        """
        クライアントから送られてきた画像の推論を行う。

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            input_data (Image.Image | str): 推論するデータ
            output_image_name (str): 出力画像のファイル名
            nodraw (bool): 描画フラグ
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if input_data is None:
            self.logger.warn(f"input_data is empty.")
            self.redis_cli.rpush(reskey, {"warn": f"input_data is empty."})
            return self.RESP_WARN
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.redis_cli.rpush(reskey, {"warn": f"{name} has not yet started a session."})
            return self.RESP_WARN
        if nodraw is None:
            nodraw = False
        session = self.sessions[name]
        try:
            predict_process_start = time.perf_counter()
            # 前処理を実行
            if session['before_injections'] is not None:
                injections:List[injection.BeforeInjection] = session['before_injections']
                for inject in injections:
                    input_data = inject.action(reskey, name, input_data, session)
            before_injections_end = time.perf_counter()
            # 推論を実行
            predict_obj:predict.Predict = session['predict_obj']
            outputs, output_image = predict_obj.predict(session['session'], session['model_img_width'], session['model_img_height'], input_data,
                                                        labels=session['labels'], colors=session['colors'], nodraw=nodraw)
            outputs['image_name'] = output_image_name
            predict_end = time.perf_counter()
            if session['tracker'] is not None:
                if 'output_boxes' in outputs and 'output_scores' in outputs and 'output_classes' in outputs:
                    detections = [Detection(box, score, cls) for box, score, cls in zip(outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'])]
                    session['tracker'].step(detections=detections)
                    tracks = session['tracker'].active_tracks()
                    outputs['output_tracks'] = [t.id for t in tracks]
                    if output_image is not None and not nodraw:
                        output_image, _ = common.draw_boxes(output_image, outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'], ids=outputs['output_tracks'])
            tracker_end = time.perf_counter()

            def _after_injection(reskey:str, name:str, output:dict, output_image:Image.Image, session:dict):
                if session['after_injections'] is not None:
                    injections:List[injection.AfterInjection] = session['after_injections']
                    for inject in injections:
                        output, output_image = inject.action(reskey, name, output, output_image, session)
                return output, output_image

            def _set_perftime(output, predict_process_start, before_injections_end, predict_end, tracker_end, after_injections_end, predict_process_end):
                performance = [dict(key="sv_before", val=f"{(before_injections_end-predict_process_start):.3f}s"),
                               dict(key="sv_predict", val=f"{(predict_end-before_injections_end):.3f}s"),
                               dict(key="sv_track", val=f"{(tracker_end-predict_end):.3f}s"),
                               dict(key="sv_after", val=f"{(after_injections_end-tracker_end):.3f}s"),
                               dict(key="sv_process", val=f"{(predict_process_end-predict_process_start):.3f}s")]
                if 'success' in output:
                    output['success']['performance'] = performance

            if output_image is not None:
                output = dict(success=outputs, output_image_name=output_image_name)
                output_image_npy = convert.img2npy(output_image)
                output_image_b64 = convert.npy2b64str(output_image_npy)
                output['output_image'] = output_image_b64
                output['output_image_shape'] = output_image_npy.shape
                predict_process_end = time.perf_counter()
                # 後処理を実行
                output, output_image = _after_injection(reskey, name, output, output_image, session)
                after_injections_end = time.perf_counter()
                _set_perftime(output, predict_process_start, before_injections_end, predict_end,
                             tracker_end, after_injections_end, predict_process_end)
                self.redis_cli.rpush(reskey, output)
                return self.RESP_SCCESS
            output = dict(success=outputs)
            # 後処理を実行
            output, _ = _after_injection(reskey, name, output, None, session)
            after_injections_end = predict_process_end = time.perf_counter()
            _set_perftime(output, predict_process_start, before_injections_end, predict_end,
                            tracker_end, after_injections_end, predict_process_end)
            self.redis_cli.rpush(reskey, output)
            return self.RESP_SCCESS
        except Exception as e:
            self.logger.warn(f"Failed to run inference: {e}", exc_info=True)
            self.redis_cli.rpush(reskey, {"warn": f"Failed to run inference: {e}"})
            return self.RESP_WARN

    def file_list(self, reskey:str, current_path:str) -> int:
        """
        ファイルリストを取得する

        Args:
            reskey (str): レスポンスキー
            path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_list(current_path)
        self.redis_cli.rpush(reskey, msg)
        return rescode

    def file_mkdir(self, reskey:str, current_path:str) -> int:
        """
        ディレクトリを作成する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_mkdir(current_path)
        self.redis_cli.rpush(reskey, msg)
        return rescode
    
    def file_rmdir(self, reskey:str, current_path:str) -> int:
        """
        ディレクトリを削除する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_rmdir(current_path)
        self.redis_cli.rpush(reskey, msg)
        return rescode

    def file_download(self, reskey:str, current_path:str) -> int:
        """
        ファイルをダウンロードする

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_download(current_path)
        self.redis_cli.rpush(reskey, msg)
        return rescode

    def file_upload(self, reskey:str, current_path:str, file_name:str, file_data:bytes, mkdir:bool, orverwrite:bool) -> int:
        """
        ファイルをアップロードする

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス
            file_name (str): ファイル名
            file_data (bytes): ファイルデータ
            mkdir (bool): ディレクトリを作成するかどうか
            orverwrite (bool): 上書きするかどうか

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_upload(current_path, file_name, file_data, mkdir, orverwrite)
        self.redis_cli.rpush(reskey, msg)
        return rescode

    def file_remove(self, reskey:str, current_path:str) -> int:
        """
        ファイルを削除する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        rescode, msg = super().file_remove(current_path)
        self.redis_cli.rpush(reskey, msg)
        return rescode
