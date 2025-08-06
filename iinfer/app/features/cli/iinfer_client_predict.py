from cmdbox.app import common, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from motpy import Detection
from iinfer.app import common as cmn, client, injection, predict
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from PIL import Image
import argparse
import cv2
import logging
import sys
import time


class ClientPredict(feature.Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'client'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'predict'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False,
            description_ja="AIモデルを指定して推論を実行します。",
            description_en="Perform inference by specifying the AI model.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(short="n", opt="name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="削除するAIモデルの登録名を指定します。",
                     description_en="Specify the registration name of the AI model to be deleted.",
                     test_true={"yolox":"yolox",
                                "upernet":"upernet",
                                "san":"san",
                                "pspnet":"pspnet",
                                "swin":"swin",
                                "lnsightface":"lnsightface",
                                "yolo3":"yolo3",
                                "effnet":"effnet",
                                "custom":"custom"}),
                dict(short="i", opt="input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="推論させる画像をファイルで指定します。",
                     description_en="Specify the image to be inferred by file.",
                     test_true={"yolox":"tests/dog.jpg",
                                "upernet":None,
                                "san":"tests/dog.jpg",
                                "pspnet":"tests/dog.jpg",
                                "swin":"tests/dog.jpg",
                                "lnsightface":"capture.csv",
                                "yolo3":"tests/dog.jpg",
                                "effnet":"tests/dog.jpg",
                                "custom":None}),
                dict(opt="stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="推論させる画像を標準入力から読み込む。",
                     description_en="Read the image to be inferred from standard input.",
                     test_true={"yolox":False,
                                "upernet":True,
                                "custom":True},
                     test_stdin={"yolox":None,
                                 "upernet":"tests/dog.jpg",
                                 "custom":"tests/dog.jpg"}),
                dict(opt="nodraw", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="推論結果画像にbbox等の描き込みを行わない。",
                     description_en="Do not draw bboxes etc. on the inference result image.",
                     test_true={"yolox":True}),
                dict(opt="pred_input_type", type=Options.T_STR, default="jpeg", required=True, multi=False, hide=False,
                        choice=['bmp', 'png', 'jpeg', 'capture', 'output_json'],
                     description_ja="推論させる入力タイプを指定します。",
                     description_en="Specifies the input type to be inferred.",
                     test_true={"yolox":"jpeg",
                                "upernet":"jpeg",
                                "san":"jpeg",
                                "pspnet":"jpeg",
                                "swin":"jpeg",
                                "lnsightface":"capture",
                                "yolo3":"jpeg",
                                "effnet":"jpeg",
                                "custom":"jpeg"}),
                dict(opt="output_image", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="推論結果画像の保存先ファイルを指定します。",
                     description_en="Specify the destination file for saving the inference result image.",
                     test_true={"yolox":"pred.jpg"}),
                dict(short="P", opt="output_preview", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="推論結果画像を `cv2.imshow` で表示します。",
                     description_en="Display the inference result image with `cv2.imshow`.",
                     test_true={"yolox":True,
                                "upernet":True,
                                "san":True,
                                "pspnet":True,
                                "swin":True,
                                "lnsightface":True,
                                "yolo3":True,
                                "effnet":True,
                                "custom":True}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds.",
                     test_true={"yolox":15,
                                "upernet":60,
                                "san":60,
                                "pspnet":60,
                                "swin":60,
                                "lnsightface":15,
                                "yolo3":15,
                                "effnet":15,
                                "custom":15}),
                dict(opt="output_json", short="o" , type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a" , type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )
    
    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'predict'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        try:
            if args.input_file is not None:
                if logger.level == logging.DEBUG:
                    logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, args.input_file={args.input_file}")
                ret = cl.predict(args.name, image_file=args.input_file, pred_input_type=args.pred_input_type,
                                        output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                if type(ret) is list:
                    for r in ret:
                        common.print_format(r, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        if logger.level == logging.DEBUG:
                            ret_str = common.to_str(r, slise=100)
                            logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                        tm = time.perf_counter()
                        args.output_json_append = True
                else:
                    common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            elif args.stdin:
                if args.pred_input_type is None:
                    msg = {"warn":f"Please specify the --pred_input_type option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if logger.level == logging.DEBUG:
                        msg_str = common.to_str(msg, slise=100)
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
                    return self.RESP_WARN, msg, cl
                if args.pred_input_type in ['capture']:
                    def _pred(args, line, tm):
                        if logger.level == logging.DEBUG:
                            line_str = common.to_str(line, slise=100)
                            logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image={line_str}")
                        ret = cl.predict(args.name, image=line, pred_input_type=args.pred_input_type,
                                            output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        if logger.level == logging.DEBUG:
                            ret_str = common.to_str(ret, slise=100)
                            logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                    for line in sys.stdin:
                        # 標準入力による推論処理は非同期で行う(同名複数serverの場合にスループットを向上させるため)
                        #thread = threading.Thread(target=_pred, args=(args, line, tm))
                        #thread.start()
                        _pred(args, line, tm)
                        tm = time.perf_counter()
                        args.output_json_append = True
                else:
                    if logger.level == logging.DEBUG:
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image=<stdin>")
                    ret = cl.predict(args.name, image=sys.stdin.buffer.read(), pred_input_type=args.pred_input_type,
                                        output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                    common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if logger.level == logging.DEBUG:
                        ret_str = common.to_str(ret, slise=100)
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                    tm = time.perf_counter()
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if logger.level == logging.DEBUG:
                    msg_str = common.to_str(msg, slise=100)
                    logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
                return self.RESP_WARN, msg, cl
        finally:
            try:
                cv2.destroyWindow('preview')
            except:
                pass

        return self.RESP_SUCCESS, None, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        nodraw = True if msg[4] == 'True' else False
        shape = [int(msg[5]), int(msg[6])]
        if int(msg[7]) > 0: shape.append(int(msg[7]))
        output_image_name = msg[8]
        if shape[0] >0 and shape[1] > 0:
            img_npy = convert.b64str2npy(msg[3], shape)
            image = convert.npy2img(img_npy)
            st = self.predict(msg[1], msg[2], image, output_image_name, nodraw,
                              data_dir, logger, redis_cli, sessions)
        else:
            st = self.predict(msg[1], msg[2], convert.b64str2str(msg[3]), output_image_name, nodraw,
                              data_dir, logger, redis_cli, sessions)

        return st

    def predict(self, reskey:str, name:str, input_data:Union[Image.Image, str], output_image_name:str, nodraw:bool,
                data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        クライアントから送られてきた画像の推論を行う。

        Args:
            reskey (str): レスポンスキー
            name (dict): モデル名
            input_data (Image.Image | str): 推論するデータ
            output_image_name (str): 出力画像のファイル名
            nodraw (bool): 描画フラグ
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        """
        if name is None or name == "":
            logger.warning(f"Name is empty.")
            redis_cli.rpush(reskey, {"warn": f"Name is empty."})
            return self.RESP_WARN
        if input_data is None:
            logger.warning(f"input_data is empty.")
            redis_cli.rpush(reskey, {"warn": f"input_data is empty."})
            return self.RESP_WARN
        if name not in sessions:
            logger.warning(f"{name} has not yet started a session.")
            redis_cli.rpush(reskey, {"warn": f"{name} has not yet started a session."})
            return self.RESP_WARN
        if nodraw is None:
            nodraw = False
        session = sessions[name]
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
                        output_image, _ = cmn.draw_boxes(output_image, outputs['output_boxes'], outputs['output_scores'], outputs['output_classes'], ids=outputs['output_tracks'])
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
                redis_cli.rpush(reskey, output)
                return self.RESP_SUCCESS
            output = dict(success=outputs)
            # 後処理を実行
            output, _ = _after_injection(reskey, name, output, None, session)
            after_injections_end = predict_process_end = time.perf_counter()
            _set_perftime(output, predict_process_start, before_injections_end, predict_end,
                            tracker_end, after_injections_end, predict_process_end)
            redis_cli.rpush(reskey, output)
            return self.RESP_SUCCESS
        except Exception as e:
            logger.warning(f"Failed to run inference: {e}", exc_info=True)
            redis_cli.rpush(reskey, {"warn": f"Failed to run inference: {e}"})
            return self.RESP_WARN
