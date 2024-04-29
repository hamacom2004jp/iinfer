from motpy import Detection, MultiObjectTracker
from pathlib import Path
from PIL import Image
from iinfer.app import common, predict, injection
from iinfer.app.commons import convert, module
from typing import List, Dict, Any, Tuple
import base64
import datetime
import logging
import json
import numpy as np
import redis
import shutil
import time


class Server(object):
    RESP_SCCESS:int = 0
    RESP_WARN:int = 1
    RESP_ERROR:int = 2
    def __init__(self, data_dir: Path, logger: logging.Logger, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = None, svname: str = 'server'):
        """
        Redisサーバーに接続し、クライアントからのコマンドを受信し実行する

        Args:
            data_dir (Path): データディレクトリのパス
            logger (logging): ロガー
            redis_host (str): Redisホスト名, by default "localhost"
            redis_port (int): Redisポート番号, by default 6379
            redis_password (str): Redisパスワード, by default None
            svname (str, optional): 推論サーバーのサービス名. by default 'server'
        """
        self.data_dir = data_dir
        self.logger = logger
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = f"sv-{svname}"
        self.hbname = f"hb-{svname}"
        self.redis_cli = None
        self.sessions:Dict[str, Dict[str, Any]] = {}
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

    def list_server(self):
        """
        起動しているサーバーリストを取得する

        Returns:
            List[str]: サーバーのリスト
        """
        self.redis_cli = redis.Redis(host=self.redis_host, port=self.redis_port, db=0, password=self.redis_password)
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
                    recive_cnt = int(self.redis_cli.hget(hb, 'recive_cnt').decode())
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    sccess_cnt = int(self.redis_cli.hget(hb, 'sccess_cnt').decode())
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    warn_cnt = int(self.redis_cli.hget(hb, 'warn_cnt').decode())
                if self.redis_cli.hexists(hb, 'sccess_cnt'):
                    error_cnt = int(self.redis_cli.hget(hb, 'error_cnt').decode())
            except redis.exceptions.ResponseError:
                self.logger.warn(f"Failed to get ctime. {hb}", exc_info=True)
            svlist.append(dict(svname=svname, recive_cnt=recive_cnt, sccess_cnt=sccess_cnt, warn_cnt=warn_cnt, error_cnt=error_cnt))
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
        self.redis_cli.hset(self.hbname, 'recive_cnt', str(recive_cnt))
        self.redis_cli.hset(self.hbname, 'sccess_cnt', str(sccess_cnt))
        self.redis_cli.hset(self.hbname, 'warn_cnt', str(warn_cnt))
        self.redis_cli.hset(self.hbname, 'error_cnt', str(error_cnt))
        while self.is_running:
            try:
                # ブロッキングリストから要素を取り出す
                ctime = time.time()
                self.redis_cli.hset(self.hbname, 'ctime', str(ctime))
                result = self.redis_cli.blpop(self.svname, timeout=1)
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
                self.redis_cli.hset(self.hbname, 'recive_cnt', str(recive_cnt))

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
                elif msg[0] == 'deploy_list':
                    st = self.deploy_list(msg[1])
                elif msg[0] == 'undeploy':
                    st = self.undeploy(msg[1], msg[2])
                elif msg[0] == 'start':
                    st = self.start(msg[1], msg[2], msg[3], (True if msg[4]=='True' else False), (None if msg[5]=='None' else msg[5]))
                elif msg[0] == 'stop':
                    st = self.stop(msg[1], msg[2])
                elif msg[0] == 'predict':
                    #byteio = BytesIO(base64.b64decode(msg[3]))
                    #img_npy = np.load(byteio)
                    nodraw = True if msg[4] == 'True' else False
                    shape = [int(msg[5]), int(msg[6])]
                    if int(msg[7]) > 0: shape.append(int(msg[7]))
                    output_image_name = msg[8]
                    img_npy = convert.b64str2npy(msg[3], shape)
                    image = convert.npy2img(img_npy)
                    st = self.predict(msg[1], msg[2], image, output_image_name, nodraw)
                elif msg[0] == 'stop_server':
                    self.is_running = False
                    self.responce(msg[1], {"success": f"Successful stop server. svname={self.svname}"})
                    break
                elif msg[0] == 'file_list':
                    st = self.file_list(msg[1], msg[2])
                elif msg[0] == 'file_mkdir':
                    st = self.file_mkdir(msg[1], msg[2])
                elif msg[0] == 'file_rmdir':
                    st = self.file_rmdir(msg[1], msg[2])
                elif msg[0] == 'file_download':
                    st = self.file_download(msg[1], msg[2])
                elif msg[0] == 'file_upload':
                    file_data = convert.b64str2bytes(msg[4])
                    st = self.file_upload(msg[1], msg[2], msg[3], file_data)
                elif msg[0] == 'file_remove':
                    st = self.file_remove(msg[1], msg[2])
                else:
                    self.logger.warn(f"Unknown command {msg}")
                    st = self.RESP_WARN

                if st==self.RESP_SCCESS:
                    sccess_cnt += 1
                    self.redis_cli.hset(self.hbname, 'sccess_cnt', str(sccess_cnt))
                elif st==self.RESP_WARN:
                    warn_cnt += 1
                    self.redis_cli.hset(self.hbname, 'warn_cnt', str(warn_cnt))
                elif st==self.RESP_ERROR:
                    error_cnt += 1
                    self.redis_cli.hset(self.hbname, 'error_cnt', str(error_cnt))
            except redis.exceptions.TimeoutError:
                pass
            except redis.exceptions.ConnectionError as e:
                self.logger.error(f"Connection to the server was lost. {e}")
                self.is_running = False
                break
            except KeyboardInterrupt as e:
                self.is_running = False
                break
            except Exception as e:
                self.logger.error(f"Unknown error occurred. {e}", exc_info=True)
                self.is_running = False
                break
        self.redis_cli.delete(self.svname)
        self.redis_cli.delete(self.hbname)
        self.logger.info(f"stop server. svname={self.svname}")

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
        self.redis_cli.rpush(reskey, json.dumps(result, default=common.default_json_enc))
        

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
            self.responce(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if model_img_width is None or model_img_width <= 0:
            self.logger.warn(f"Image width is invalid.")
            self.responce(reskey, {"warn": f"Image width is invalid."})
            return self.RESP_WARN
        if model_img_height is None or model_img_height <= 0:
            self.logger.warn(f"Image height is invalid.")
            self.responce(reskey, {"warn": f"Image height is invalid."})
            return self.RESP_WARN

        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        if not overwrite and deploy_dir.exists():
            self.logger.warn(f"Could not be deployed. '{deploy_dir}' already exists")
            self.responce(reskey, {"warn": f"Could not be deployed. '{deploy_dir}' already exists"})
            return self.RESP_WARN

        if predict_type not in common.BASE_MODELS:
            self.logger.warn(f"Incorrect predict_type. '{predict_type}'")
            self.responce(reskey, {"warn": f"Incorrect predict_type. '{predict_type}'"})
            return self.RESP_WARN
        if common.BASE_MODELS[predict_type]['required_model_conf']==True and model_conf_file is None:
            self.logger.warn(f"model_conf_file is None.")
            self.responce(reskey, {"warn": f"model_conf_file is None."})
            return self.RESP_WARN

        common.mkdirs(deploy_dir)
        def _save_s(file:str, data:bytes):
            if file is None or data is None:
                return False, None
            file = deploy_dir / file
            with open(file, "wb") as f:
                f.write(data)
                self.logger.info(f"Save {file} to {str(deploy_dir)}")
            return True, file

        if common.BASE_MODELS[predict_type]['required_model_weight']==True and (model_file is None or model_bin is None):
            self.logger.warn(f"model_file is None.")
            self.responce(reskey, {"warn": f"model_file is None."})
            return self.RESP_WARN
        else:
            ret, model_file = _save_s(model_file, model_bin)

        ret, before_injection_conf = _save_s("before_injection_conf.json", before_injection_conf)
        ret, after_injection_conf = _save_s("after_injection_conf.json", after_injection_conf)

        def _save_m(name:str, files:List[str], datas:List[bytes]):
            if files is not None and datas is None:
                self.logger.warn(f"{name}_file is not None but {name}_bin is None.")
                self.responce(reskey, {"warn": f"{name}_file is not None but {name}_bin is None."})
                return False, files
            if files is None and datas is not None:
                self.logger.warn(f"{name}_file is None but {name}_bin is not None.")
                self.responce(reskey, {"warn": f"{name}_file is None but {name}_bin is not None."})
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
                        model_file=model_file, model_conf_file=model_conf_file, custom_predict_file=(custom_predict_file if custom_predict_file is not None else None),
                        label_file=label_file, color_file=color_file, before_injection_conf=before_injection_conf, after_injection_conf=after_injection_conf,
                        before_injection_type=before_injection_type, after_injection_type=after_injection_type,
                        before_injection_py=before_injection_py, after_injection_py=after_injection_py)
            json.dump(conf, f, default=common.default_json_enc)
            self.logger.info(f"Save conf.json to {str(deploy_dir)}")

        if predict_type.startswith('mmpretrain_'):
            if not (self.data_dir / "mmpretrain").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone https://github.com/open-mmlab/mmpretrain.git', logger=self.logger)
                if returncode != 0:
                    self.logger.error(f"Failed to git clone mmpretrain.")
                    self.responce(reskey, {"error": f"Failed to git clone mmpretrain."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmpretrain" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmpretrain configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmdet_'):
            if not (self.data_dir / "mmdetection").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone https://github.com/open-mmlab/mmdetection.git', logger=self.logger)
                if returncode != 0:
                    self.logger.error(f"Failed to git clone mmdetection.")
                    self.responce(reskey, {"error": f"Failed to git clone mmdetection."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmdetection" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmdetection configs to {str(deploy_dir / 'configs')}")
        elif predict_type.startswith('mmseg_'):
            if not (self.data_dir / "mmsegmentation").exists():
                returncode, _ = common.cmd(f'cd {self.data_dir} && git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=self.logger)
                if returncode != 0:
                    self.logger.error(f"Failed to git clone mmsegmentation.")
                    self.responce(reskey, {"error": f"Failed to git clone mmsegmentation."})
                    return self.RESP_ERROR
            shutil.copytree(self.data_dir / "mmsegmentation" / "configs", deploy_dir / "configs", dirs_exist_ok=True)
            self.logger.info(f"Copy mmsegmentation configs to {str(deploy_dir / 'configs')}")

        self.responce(reskey, {"success": f"Save conf.json to {str(deploy_dir)}"})
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
                custom_predict_file = 'exists' if "custom_predict_file" in conf and conf["custom_predict_file"] is not None and Path(conf["custom_predict_file"]).exists() else None
                label_file = 'exists' if "label_file" in conf and conf["label_file"] is not None and Path(conf["label_file"]).exists() else None
                color_file = 'exists' if "color_file" in conf and conf["color_file"] is not None and Path(conf["color_file"]).exists() else None
                row = dict(name=dir.name,
                           input=(conf["model_img_width"], conf["model_img_height"]), model_file=model_file.name, model_conf_file=model_conf_file,
                           predict_type=conf["predict_type"], custom_predict=custom_predict_file,
                           label_file=label_file, color_file=color_file,
                           session=dir.name in self.sessions,
                           mot=dir.name in self.sessions and self.sessions[dir.name]['tracker'] is not None,
                           before_injection_py=before_injection,
                           after_injection_py=after_injection)
                deploy_list.append(row)
        self.responce(reskey, {"success": deploy_list})
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
            self.responce(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        deploy_dir = self.data_dir / name
        if not deploy_dir.exists():
            self.logger.warn(f"{name} is not deployed.")
            self.responce(reskey, {"warn": f"{name} is not deployed."})
            return self.RESP_WARN
        common.rmdirs(deploy_dir)
        self.responce(reskey, {"success": f"Undeployed {name}. {str(deploy_dir)}"})
        return self.RESP_SCCESS

    def start(self, reskey:str, name:str, model_provider:str, use_track:bool, gpuid:int):
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
            self.responce(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        deploy_dir = self.data_dir / name
        if name in self.sessions:
            self.logger.warn(f"{name} has already started a session.")
            self.responce(reskey, {"warn": f"{name} has already started a session."})
            return self.RESP_WARN
        conf_path = deploy_dir / "conf.json"
        if not conf_path.exists():
            self.logger.warn(f"Conf path {str(conf_path)} does not exist")
            self.responce(reskey, {"warn": f"Conf path {str(conf_path)} does not exist"})
            return self.RESP_WARN
        with open(conf_path, "r") as cf:
            conf = json.load(cf)
            model_path = Path(conf["model_file"])
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
                self.responce(reskey, {"warn": f"Failed to load before_injection: {e}"})
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
                if not model_path.exists():
                    self.logger.warn(f"Model path {str(model_path)} does not exist")
                    self.responce(reskey, {"warn": f"Model path {str(model_path)} does not exist"})
                    return self.RESP_WARN
            except Exception as e:
                self.logger.warn(f"Failed to load after_injection: {e}", exc_info=True)
                self.responce(reskey, {"warn": f"Failed to load after_injection: {e}"})
                return self.RESP_WARN
            try:
                if conf["predict_type"] == 'Custom':
                    custom_predict_py = Path(conf["custom_predict_file"]) if conf["custom_predict_file"] is not None else None
                    if custom_predict_py is None:
                        self.logger.warn(f"predict_type is Custom but custom_predict_py is None.")
                        self.responce(reskey, {"warn": f"predict_type is Custom but custom_predict_py is None."})
                        return self.RESP_WARN
                    if not custom_predict_py.exists():
                        self.logger.warn(f"custom_predict_py path {str(custom_predict_py)} does not exist")
                        self.responce(reskey, {"warn": f"custom_predict_py path {str(custom_predict_py)} does not exist"})
                        return self.RESP_WARN
                    predict_obj = module.load_custom_predict(custom_predict_py, self.logger)
                else:
                    predict_obj = module.load_predict(conf["predict_type"], self.logger)
            except Exception as e:
                self.logger.warn(f"Failed to load Predict: {e}", exc_info=True)
                self.responce(reskey, {"warn": f"Failed to load Predict: {e}"})
                return self.RESP_WARN
            if "label_file" in conf and conf["label_file"] is not None:
                label_file = Path(conf["label_file"])
                if not label_file.exists():
                    self.logger.warn(f"label_file path {str(label_file)} does not exist")
                    self.responce(reskey, {"warn": f"label_file path {str(label_file)} does not exist"})
                    return self.RESP_WARN
                with open(label_file, "r") as f:
                    labels = f.read().splitlines()
            else:
                labels = None
            if "color_file" in conf and conf["color_file"] is not None:
                color_file = Path(conf["color_file"])
                if not color_file.exists():
                    self.logger.warn(f"color_file path {str(color_file)} does not exist")
                    self.responce(reskey, {"warn": f"color_file path {str(color_file)} does not exist"})
                    return self.RESP_WARN
                with open(color_file, "r") as f:
                    colors = f.read().splitlines()
            else:
                colors = None
            try:
                session = predict_obj.create_session(model_path, model_conf_path, model_provider, gpu_id=gpuid)
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
                self.responce(reskey, {"warn": f"Failed to create session: {e}"})
                return self.RESP_WARN
        self.logger.info(f"Successful start of {name} session.")
        self.responce(reskey, {"success": f"Successful start of {name} session."})
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
            self.responce(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.responce(reskey, {"warn": f"{name} has not yet started a session."})
            return self.RESP_WARN
        #self.sessions[name]['session'].close()
        del self.sessions[name]
        self.logger.info(f"Successful stop of {name} session.")
        self.responce(reskey, {"success": f"Successful stop of {name} session."})
        return self.RESP_SCCESS

    def predict(self, reskey:str, name:str, image:Image.Image, output_image_name:str, nodraw:bool):
        """
        クライアントから送られてきた画像の推論を行う。

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            image (Image.Image): 推論する画像データ
            output_image_name (str): 出力画像のファイル名
            nodraw (bool): 描画フラグ
        """
        if name is None or name == "":
            self.logger.warn(f"Name is empty.")
            self.responce(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if image is None:
            self.logger.warn(f"img_npy is empty.")
            self.responce(reskey, {"warn": f"img_npy is empty."})
            return self.RESP_WARN
        if name not in self.sessions:
            self.logger.warn(f"{name} has not yet started a session.")
            self.responce(reskey, {"warn": f"{name} has not yet started a session."})
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
                    image = inject.action(reskey, name, image, session)
            before_injections_end = time.perf_counter()
            # 推論を実行
            predict_obj:predict.Predict = session['predict_obj']
            outputs, output_image = predict_obj.predict(session['session'], session['model_img_width'], session['model_img_height'], image,
                                                        labels=session['labels'], colors=session['colors'], nodraw=nodraw)
            outputs['image_name'] = output_image_name
            predict_end = time.perf_counter()
            if session['tracker'] is not None:
                if 'output_boxes' in outputs and 'output_scores' in outputs and 'output_classes' in outputs:
                    detections = [Detection(box, score, cls) for box, score, cls in zip(outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'])]
                    session['tracker'].step(detections=detections)
                    tracks = session['tracker'].active_tracks()
                    outputs['output_tracks'] = [t.id for t in tracks]
                    if image is not None:
                        image = common.draw_boxes(image, outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'], ids=outputs['output_tracks'])
            tracker_end = time.perf_counter()

            def _after_injection(reskey:str, name:str, output:dict, output_image:Image.Image, session:dict):
                if session['after_injections'] is not None:
                    injections:List[injection.AfterInjection] = session['after_injections']
                    for inject in injections:
                        output, output_image = inject.action(reskey, name, output, output_image, session)
                return output, output_image

            def _set_perftime(output, predict_process_start, before_injections_end, predict_end, tracker_end, after_injections_end, predict_process_end):
                performance = f"before={(before_injections_end-predict_process_start):.3f}s" \
                              f", predict={(predict_end-before_injections_end):.3f}s" \
                              f", track={(tracker_end-predict_end):.3f}s" \
                              f", after={(after_injections_end-tracker_end):.3f}s" \
                              f", process={(predict_process_end-predict_process_start):.3f}s"
                if 'success' in output:
                    output['success']['performance'] = performance

            if output_image is not None:
                output = dict(success=outputs, output_image_name=output_image_name)
                # 後処理を実行
                output, output_image = _after_injection(reskey, name, output, output_image, session)
                after_injections_end = time.perf_counter()
                output_image_npy = convert.img2npy(output_image)
                output_image_b64 = convert.npy2b64str(output_image_npy)
                predict_process_end = time.perf_counter()
                output['output_image'] = output_image_b64
                output['output_image_shape'] = output_image_npy.shape
                _set_perftime(output, predict_process_start, before_injections_end, predict_end,
                             tracker_end, after_injections_end, predict_process_end)
                self.responce(reskey, output)
                return self.RESP_SCCESS
            output = dict(success=outputs)
            # 後処理を実行
            output, _ = _after_injection(reskey, name, output, None, session)
            after_injections_end = predict_process_end = time.perf_counter()
            _set_perftime(output, predict_process_start, before_injections_end, predict_end,
                            tracker_end, after_injections_end, predict_process_end)
            self.responce(reskey, output)
            return self.RESP_SCCESS
        except Exception as e:
            self.logger.warn(f"Failed to run inference: {e}", exc_info=True)
            self.responce(reskey, {"warn": f"Failed to run inference: {e}"})
            return self.RESP_WARN

    def _file_exists(self, reskey:str, current_path:str, not_exists:bool=False, exists_chk:bool=True) -> Tuple[bool, Path]:
        """
        パスが存在するかどうかを確認する

        Args:
            reskey (str): レスポンスキー
            current_path (str): パス
            not_exists (bool, optional): パスが存在しないことを確認するかどうか, by default False
            exists_chk (bool, optional): パス存在チェックを行うかどうか, by default True
        
        Returns:
            bool: not_existsがFalseの時パスが存在すればTrue、存在しなければFalse。not_existsがTrueの時パスが存在しなければTrue、存在すればFalse。
            Path: データフォルダ以下のcurrent_pathを含めた絶対パス
        """
        if current_path is None or current_path == "":
            self.logger.warn(f"current_path is empty.")
            self.responce(reskey, {"warn": f"current_path is empty."})
            return False, None
        current_path = current_path.replace("\\","/")
        cp = current_path[1:] if current_path.startswith('/') else current_path
        abspath:Path = (self.data_dir / cp).resolve()
        if not str(abspath).startswith(str(self.data_dir)):
            self.logger.warn(f"Path {abspath} is out of data directory. current_path={current_path}")
            self.responce(reskey, {"warn": f"Path {abspath} is out of data directory. current_path={current_path}"})
            return False, None
        if not exists_chk:
            return True, abspath
        if not not_exists and not abspath.exists():
            self.logger.warn(f"Path {abspath} does not exist. param={current_path}")
            self.responce(reskey, {"warn": f"Path {abspath} does not exist. param={current_path}"})
            return False, None
        if not_exists and abspath.exists():
            self.logger.warn(f"Path {abspath} exist. param={current_path}")
            self.responce(reskey, {"warn": f"Path {abspath} exist. param={current_path}"})
            return False, None
        return True, abspath

    def file_list(self, reskey:str, current_path:str):
        """
        ファイルリストを取得する

        Args:
            reskey (str): レスポンスキー
            path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        chk, _ = self._file_exists(reskey, current_path)
        if not chk: return self.RESP_WARN
        
        def _ts2str(ts):
            return datetime.datetime.fromtimestamp(ts)

        current_path = f'/{current_path}' if not current_path.startswith('/') else current_path
        current_path_parts = current_path.split("/")
        current_path_parts = current_path_parts[1:] if current_path=='/' else current_path_parts
        path_tree = {}
        data_dir_len = len(str(self.data_dir))
        for i, cpart in enumerate(current_path_parts):
            cpath = '/'.join(current_path_parts[1:i+1])
            file_list:Path = self.data_dir / cpath
            children = dict()
            for f in file_list.iterdir():
                parts = str(f)[data_dir_len:].replace("\\","/").split("/")
                path = "/".join(parts[:i+2])
                key = common.safe_fname(path)
                if key in children:
                    continue
                children[key] = dict(name=f.name, is_dir=f.is_dir(), path=path, size=f.stat().st_size , last=_ts2str(f.stat().st_mtime))

            tpath = '/'.join(current_path_parts[:i+1])
            tpath = '/' if tpath=='' else tpath
            tpath_key = common.safe_fname(tpath)
            cpart = '/' if cpart=='' else cpart
            path_tree[tpath_key] = dict(name=cpart, is_dir=True, path=tpath, children=children, size=0, last="")

        self.responce(reskey, {"success": path_tree})
        return self.RESP_SCCESS

    def file_mkdir(self, reskey:str, current_path:str):
        """
        ディレクトリを作成する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
        """
        chk, abspath = self._file_exists(reskey, current_path, not_exists=True)
        if not chk: return self.RESP_WARN

        abspath.mkdir(parents=True)
        ret_path = str(Path(current_path).parent).replace("\\","/")
        self.responce(reskey, {"success": {"path":f"{ret_path}","msg":f"Created {abspath}"}})
        return self.RESP_SCCESS
    
    def file_rmdir(self, reskey:str, current_path:str):
        """
        ディレクトリを削除する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
        """
        chk, abspath = self._file_exists(reskey, current_path)
        if not chk: return self.RESP_WARN
        if abspath == self.data_dir:
            self.logger.warn(f"Path {abspath} is root directory.")
            self.responce(reskey, {"warn": f"Path {abspath} is root directory."})
            return self.RESP_WARN

        common.rmdirs(abspath)
        ret_path = str(Path(current_path).parent).replace("\\","/")
        self.responce(reskey, {"success": {"path":f"{ret_path}","msg":f"Removed {abspath}"}})
        return self.RESP_SCCESS

    def file_download(self, reskey:str, current_path:str):
        """
        ファイルをダウンロードする

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        chk, abspath = self._file_exists(reskey, current_path)
        if not chk: return self.RESP_WARN
        if abspath.is_dir():
            self.logger.warn(f"Path {abspath} is directory.")
            self.responce(reskey, {"warn": f"Path {abspath} is directory."})
            return self.RESP_WARN

        with open(abspath, "rb") as f:
            data = convert.bytes2b64str(f.read())
            self.responce(reskey, {"success":{"name":abspath.name, "data":data}})
        return self.RESP_SCCESS
    
    def file_upload(self, reskey:str, current_path:str, file_name:str, file_data:bytes):
        """
        ファイルをアップロードする

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス
            file_name (str): ファイル名
            file_data (bytes): ファイルデータ

        Returns:
            int: レスポンスコード
        """
        chk, abspath = self._file_exists(reskey, current_path, exists_chk=False)
        if not chk:
            return self.RESP_WARN

        if abspath.exists():
            if abspath.is_dir():
                abspath = abspath / file_name
            if abspath.is_file():
                self.logger.warn(f"Path {abspath} already exist. param={current_path}")
                self.responce(reskey, {"warn": f"Path {abspath} already exist. param={current_path}"})
                return self.RESP_WARN
            save_path = abspath
        elif abspath.suffix == '':
            abspath.mkdir(parents=True, exist_ok=True)
            save_path = abspath / file_name
        else:
            save_path = abspath

        with open(save_path, "wb") as f:
            f.write(file_data)
            self.responce(reskey, {"success": f"Uploaded {save_path}"})
        return self.RESP_SCCESS

    def file_remove(self, reskey:str, current_path:str) -> int:
        """
        ファイルを削除する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス

        Returns:
            int: レスポンスコード
        """
        chk, abspath = self._file_exists(reskey, current_path)
        if not chk: return self.RESP_WARN
        if abspath.is_dir():
            self.logger.warn(f"Path {abspath} is directory.")
            self.responce(reskey, {"warn": f"Path {abspath} is directory."})
            return self.RESP_WARN

        abspath.unlink()
        ret_path = str(Path(current_path).parent).replace("\\","/")
        self.responce(reskey, {"success": {"path":f"{ret_path}","msg":f"Removed {abspath}"}})
        return self.RESP_SCCESS
    