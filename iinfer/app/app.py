from iinfer import version
from iinfer.app import common, client, install, options, postprocess, redis, server, web
from iinfer.app.postprocesses import cls_jadge, cmd, csv, det_clip, det_face_store, det_filter, det_jadge, httpreq, seg_bbox, seg_filter, showimg
from pathlib import Path
import argparse
import argcomplete
import cv2
import logging
import sys
import time
import traceback
import threading


def main(args_list:list=None):
    app = IinferApp()
    return app.main(args_list)[0]

class IinferApp:
    def __init__(self):
        self.sv = None
        self.cl = None
        self.web = None

    def main(self, args_list:list=None, file_dict:dict=dict()):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        parser = argparse.ArgumentParser(prog='iinfer', description='This application generates modules to set up the application system.')
        opts = options.Options().list_options()
        for opt in opts.values():
            default = opt["default"] if opt["default"] is not None and opt["default"] != "" else None
            if opt["action"] is None:
                parser.add_argument(*opt["opts"], help=opt["help"], type=opt["type"], default=default, choices=opt["choices"])
            else:
                parser.add_argument(*opt["opts"], help=opt["help"], default=default, action=opt["action"])

        argcomplete.autocomplete(parser)
        # mainメソッドの起動時引数がある場合は、その引数を解析する
        if args_list is not None:
            args = parser.parse_args(args=args_list)
        else:
            args = parser.parse_args()
        # 起動時引数で指定されたオプションをファイルから読み込んだオプションで上書きする
        args_dict = vars(args)
        for key, val in file_dict.items():
            args_dict[key] = val
        # useoptオプションで指定されたオプションファイルを読み込む
        opt = common.loadopt(args.useopt)
        # 最終的に使用するオプションにマージする
        for key, val in args_dict.items():
            args_dict[key] = common.getopt(opt, key, preval=args_dict, withset=True)
        args = argparse.Namespace(**args_dict)

        tm = time.perf_counter()
        ret = {"success":f"Start command. {args}"}

        if args.saveopt:
            if args.useopt is None:
                msg = {"warn":f"Please specify the --useopt option."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg
            common.saveopt(opt, args.useopt)
            ret = {"success":f"Save options file. {args.useopt}"}

        if args.version:
            v = version.__logo__ + '\n' + version.__description__
            common.print_format(v, False, tm, None, False)
            return 0, v

        if args.mode is None:
            msg = {"warn":f"mode is None. Please specify the --help option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg

        common.mklogdir(args.data)
        common.copy_sample(args.data)
        common.copy_sample(Path.cwd())

        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data)
        if logger.level == logging.DEBUG:
            logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}")
        if args.mode == 'server':
            if args.cmd == 'start':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                if args.svname is None:
                    msg = {"warn":f"Please specify the --svname option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                self.sv = server.Server(Path(args.data), logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                self.sv.start_server(args.retry_count, args.retry_interval)
            elif args.cmd == 'stop':
                if args.svname is None:
                    msg = {"warn":f"Please specify the --svname option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                ret = cl.stop_server(retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            elif args.cmd == 'list':
                self.sv = server.Server(Path(args.data), logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname='server') # list取得なのでデフォルトのsvnameを指定
                ret = self.sv.list_server()
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'gui':
            if args.cmd == 'start':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                #self.web = gui.Gui(logger, Path(args.data))
                self.web = web.Web(logger, Path(args.data), redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                                   client_only=args.client_only, filer_html=args.filer_html, showimg_html=args.showimg_html, webcap_html=args.webcap_html,
                                   anno_html=args.anno_html, assets=args.assets, gui_mode=True)
                self.web.start()
                msg = {"success":"eel web complate."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 0, msg
            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'web':
            if args.cmd == 'start':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                try:
                    self.web = web.Web(logger, Path(args.data), redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                                    client_only=args.client_only, filer_html=args.filer_html, showimg_html=args.showimg_html, webcap_html=args.webcap_html,
                                    anno_html=args.anno_html, assets=args.assets)
                    self.web.start(args.allow_host, args.listen_port, outputs_key=args.outputs_key)
                    msg = {"success":"web complate."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 0, msg
                except Exception as e:
                    msg = {"warn":f"Web server start error. {traceback.format_exc()}"}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
            elif args.cmd == 'stop':
                self.web = web.Web(logger, Path(args.data))
                self.web.stop()
                msg = {"success":"web complate."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 0, msg
            elif args.cmd == 'webcap':
                self.web = web.Web(logger, Path(args.data))
                try:
                    self.web.webcap(args.allow_host, args.listen_port, image_type=args.image_type, outputs_key=args.outputs_key,
                                    capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                                    capture_count=args.capture_count, capture_fps=args.capture_fps)
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg
            
        elif args.mode == 'client':
            if args.svname is None:
                msg = {"warn":f"Please specify the --svname option."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg
            self.cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            if args.cmd == 'deploy':
                if args.model_conf_file is not None:
                    args.model_conf_file = [Path(f) for f in args.model_conf_file if f is not None and f != '']
                if args.before_injection_py is not None:
                    args.before_injection_py = [Path(f) for f in args.before_injection_py if f is not None and f != '']
                if args.after_injection_py is not None:
                    args.after_injection_py = [Path(f) for f in args.after_injection_py if f is not None and f != '']
                args.custom_predict_py = Path(args.custom_predict_py) if args.custom_predict_py is not None else None
                args.label_file = Path(args.label_file) if args.label_file is not None else None
                args.color_file = Path(args.color_file) if args.color_file is not None else None
                args.before_injection_conf = Path(args.before_injection_conf) if args.before_injection_conf is not None else None
                args.after_injection_conf = Path(args.after_injection_conf) if args.after_injection_conf is not None else None

                args.train_dataset = Path(args.train_dataset) if args.train_dataset is not None else None
                args.custom_train_py = Path(args.custom_train_py) if args.custom_train_py is not None else None

                ret = self.cl.deploy(args.name, args.model_img_width, args.model_img_height, args.model_file, args.model_conf_file, args.predict_type,
                                args.custom_predict_py, label_file=args.label_file, color_file=args.color_file,
                                before_injection_conf=args.before_injection_conf, before_injection_type=args.before_injection_type, before_injection_py=args.before_injection_py,
                                after_injection_conf=args.after_injection_conf, after_injection_type=args.after_injection_type, after_injection_py=args.after_injection_py,
                                train_dataset=args.train_dataset, train_dataset_upload=args.train_dataset_upload, train_type=args.train_type, custom_train_py=args.custom_train_py,
                                overwrite=args.overwrite, retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'train':
                ret = self.cl.train(args.name, overwrite=args.overwrite,
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'deploy_list':
                ret = self.cl.deploy_list(retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'undeploy':
                ret = self.cl.undeploy(args.name, retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'start':
                ret = self.cl.start(args.name, model_provider=args.model_provider, use_track=args.use_track, gpuid=args.gpuid,
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'stop':
                ret = self.cl.stop(args.name,
                                   retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'predict':
                try:
                    if args.input_file is not None:
                        if self.cl.logger.level == logging.DEBUG:
                            self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, args.input_file={args.input_file}")
                        ret = self.cl.predict(args.name, image_file=args.input_file, pred_input_type=args.pred_input_type,
                                                output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                                retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                        if type(ret) is list:
                            for r in ret:
                                common.print_format(r, args.format, tm, args.output_json, args.output_json_append)
                                if self.cl.logger.level == logging.DEBUG:
                                    ret_str = common.to_str(r, slise=100)
                                    self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                                tm = time.perf_counter()
                                args.output_json_append = True
                        else:
                            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                    elif args.stdin:
                        if args.pred_input_type is None:
                            msg = {"warn":f"Please specify the --pred_input_type option."}
                            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                            if self.cl.logger.level == logging.DEBUG:
                                msg_str = common.to_str(msg, slise=100)
                                self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
                            return 1, msg
                        if args.pred_input_type in ['capture']:
                            def _pred(args, line, tm):
                                if self.cl.logger.level == logging.DEBUG:
                                    line_str = common.to_str(line, slise=100)
                                    self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image={line_str}")
                                ret = self.cl.predict(args.name, image=line, pred_input_type=args.pred_input_type,
                                                      output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                                      retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                                if self.cl.logger.level == logging.DEBUG:
                                    ret_str = common.to_str(ret, slise=100)
                                    self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                            for line in sys.stdin:
                                # 標準入力による推論処理は非同期で行う(同名複数serverの場合にスループットを向上させるため)
                                #thread = threading.Thread(target=_pred, args=(args, line, tm))
                                #thread.start()
                                _pred(args, line, tm)
                                tm = time.perf_counter()
                                args.output_json_append = True
                        else:
                            if self.cl.logger.level == logging.DEBUG:
                                self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image=<stdin>")
                            ret = self.cl.predict(args.name, image=sys.stdin.buffer.read(), pred_input_type=args.pred_input_type,
                                                  output_image_file=args.output_image, output_preview=args.output_preview, nodraw=args.nodraw,
                                                  retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                            if self.cl.logger.level == logging.DEBUG:
                                ret_str = common.to_str(ret, slise=100)
                                self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                            tm = time.perf_counter()
                    else:
                        msg = {"warn":f"Image file or stdin is empty."}
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                        if self.cl.logger.level == logging.DEBUG:
                            msg_str = common.to_str(msg, slise=100)
                            self.cl.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
                        return 1, msg
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass

            elif args.cmd == 'file_list':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                ret = self.cl.file_list(args.svpath.replace('"',''), scope=args.scope, client_data=client_data,
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_mkdir':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                ret = self.cl.file_mkdir(args.svpath.replace('"',''), scope=args.scope, client_data=client_data,
                                         retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_rmdir':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                ret = self.cl.file_rmdir(args.svpath.replace('"',''), scope=args.scope, client_data=client_data,
                                         retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_download':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                download_file = Path(args.download_file.replace('"','')) if args.download_file is not None else None
                ret = self.cl.file_download(args.svpath.replace('"',''), download_file, scope=args.scope, client_data=client_data, rpath=args.rpath, img_thumbnail=args.img_thumbnail,
                                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_upload':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                upload_file = Path(args.upload_file.replace('"','')) if args.upload_file is not None else None
                ret = self.cl.file_upload(args.svpath.replace('"',''), upload_file, scope=args.scope, client_data=client_data,
                                          mkdir=args.mkdir, orverwrite=args.orverwrite,
                                          retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'file_remove':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                ret = self.cl.file_remove(args.svpath.replace('"',''), scope=args.scope, client_data=client_data,
                                          retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_copy':
                client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
                ret = self.cl.file_copy(args.from_path.replace('"',''), args.to_path.replace('"',''), orverwrite=args.orverwrite,
                                        scope=args.scope, client_data=client_data,
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'predict_type_list':
                type_list = [dict(predict_type=key, site=val['site'], image_width=val['image_width'], image_height=val['image_height'],
                                required_model_conf=val['required_model_conf'], required_model_weight=val['required_model_weight'],
                                model_type=f"{val['model_type'].__module__}.{val['model_type'].__name__}") for key,val in common.BASE_MODELS.items()]
                type_list.append(dict(predict_type='Custom', site='Custom', image_width=None, image_height=None,
                                      required_model_conf=None, required_model_weight=None))
                ret = dict(success=type_list)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

            elif args.cmd == 'train_type_list':
                type_list = [dict(train_type=key, site=val['site'],
                                  model_type=f"{val['model_type'].__module__}.{val['model_type'].__name__}") for key,val in common.BASE_TRAIN_MODELS.items()]
                type_list.append(dict(train_type='Custom', site='Custom'))
                ret = dict(success=type_list)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

            elif args.cmd == 'read_dir':
                root_dir = Path(args.root_dir) if args.root_dir is not None else Path('.')
                moveto = Path(args.moveto) if args.moveto is not None else None
                try:
                    for t,b64,h,w,c,fn in self.cl.read_dir(args.glob_str, read_input_type=args.read_input_type, image_type=args.image_type,
                                                        root_dir=root_dir, include_hidden=args.include_hidden, moveto=moveto,
                                                        polling=args.polling, polling_count=args.polling_count, polling_interval=args.polling_interval):
                        ret = f"{t},"+b64+f",{h},{w},{c},{fn}"
                        if args.output_csv is not None:
                            with open(args.output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                                print(ret, file=f)
                                append = True
                        else:
                            common.print_format(ret, False, tm, None, False)
                except Exception as e:
                    msg = {"warn":f"{e}"}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg

            elif args.cmd == 'capture':
                count = 0
                append = False
                try:
                    for t,b64,h,w,c,fn in self.cl.capture(capture_device=args.capture_device, image_type=args.image_type,
                                        capture_frame_width=args.capture_frame_width, capture_frame_height=args.capture_frame_height,
                                        capture_fps=args.capture_fps, output_preview=args.output_preview):
                        ret = f"{t},"+b64+f",{h},{w},{c},{fn}"
                        if args.output_csv is not None:
                            with open(args.output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                                print(ret, file=f)
                                append = True
                        else: common.print_format(ret, False, tm, None, False)
                        tm = time.perf_counter()
                        count += 1
                        if args.capture_count > 0 and count >= args.capture_count:
                            break
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'postprocess':
            def _to_proc(f, proc:postprocess.Postprocess, timeout, format, tm,
                         output_json, output_json_append, output_image_file=None, output_csv=None):
                try:
                    ret = None
                    for line in f:
                        line = line.rstrip()
                        if line == "":
                            continue
                        try:
                            if proc.logger.level == logging.DEBUG:
                                line_str = common.to_str(line, slise=100)
                                proc.logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, proc={proc}, line={line_str}")
                            ret = proc.postprocess(line, output_image_file=output_image_file, timeout=timeout)
                            if output_csv is not None:
                                with open(output_csv, 'a' if output_json_append else 'w', encoding="utf-8") as f:
                                    txt = common.print_format(ret, format, tm, output_json, output_json_append, stdout=False)
                                    print(txt.strip(), file=f)
                            else: common.print_format(ret, format, tm, output_json, output_json_append)
                        except Exception as e:
                            msg = {"warn":f"Invalid input. {e}"}
                            common.print_format(msg, format, tm, output_json, output_json_append)
                            ret = msg
                        tm = time.perf_counter()
                        output_json_append = True
                    return ret
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass

            def _exec_proc(input_file, stdin, proc:postprocess.Postprocess, timeout, format, tm,
                           output_json, output_json_append, output_image_file=None, output_csv=None):
                if input_file is not None:
                    with open(input_file, 'r', encoding="UTF-8") as f:
                        ret = _to_proc(f, proc, timeout, format, tm, output_json, output_json_append,
                                       output_image_file=output_image_file, output_csv=output_csv)
                elif stdin:
                    ret = _to_proc(sys.stdin, proc, timeout, format, tm, output_json, output_json_append,
                                   output_image_file=output_image_file, output_csv=output_csv)
                else:
                    msg = {"warn":f"Image file or stdin is empty."}
                    common.print_format(msg, format, tm, output_json, output_json_append)
                    return 1, msg
                return 0, ret

            if args.cmd == 'cls_jadge':
                try:
                    proc = cls_jadge.ClaJadge(logger, ok_score_th=args.ok_score_th, ok_classes=args.ok_classes, ok_labels=args.ok_labels,
                                            ng_score_th=args.ng_score_th, ng_classes=args.ng_classes, ng_labels=args.ng_labels,
                                            ext_score_th=args.ext_score_th, ext_classes=args.ext_classes, ext_labels=args.ext_labels,
                                            nodraw=args.nodraw, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'cmd':
                try:
                    proc = cmd.Cmd(logger, cmdline=args.cmdline, output_image_ext=args.output_image_ext, output_maxsize=args.output_maxsize)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, None, False)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       None, False, output_image_file=None, output_csv=None)
                if code != 0:
                    return code, ret

            elif args.cmd == 'csv':
                try:
                    proc = csv.Csv(logger, out_headers=args.out_headers, noheader=args.noheader)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                       None, False, output_image_file=None, output_csv=args.output_csv)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_clip':
                try:
                    proc = det_clip.DetClip(logger, image_type=args.image_type, clip_margin=args.clip_margin)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                       None, False, output_image_file=None, output_csv=args.output_csv)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_face_store':
                try:
                    proc = det_face_store.DetFaceStore(logger, face_threshold=args.face_threshold, image_type=args.image_type,
                                                       clip_margin=args.clip_margin)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, False, tm,
                                       args.output_json, args.output_json_append, output_image_file=None)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_filter':
                try:
                    proc = det_filter.DetFilter(logger, score_th=args.score_th, width_th=args.width_th, height_th=args.height_th,
                                                classes=args.classes, labels=args.labels, nodraw=args.nodraw, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_jadge':
                try:
                    proc = det_jadge.DetJadge(logger, ok_score_th=args.ok_score_th, ok_classes=args.ok_classes, ok_labels=args.ok_labels,
                                            ng_score_th=args.ng_score_th, ng_classes=args.ng_classes, ng_labels=args.ng_labels,
                                            ext_score_th=args.ext_score_th, ext_classes=args.ext_classes, ext_labels=args.ext_labels,
                                            nodraw=args.nodraw, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'httpreq':
                try:
                    proc = httpreq.Httpreq(logger, fileup_name=args.fileup_name, json_without_img=args.json_without_img)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       None, False, output_image_file=None)
                if code != 0:
                    return code, ret

            elif args.cmd == 'seg_bbox':
                try:
                    proc = seg_bbox.SegBBox(logger, del_segments=args.del_segments, nodraw=args.nodraw,
                                            nodraw_bbox=args.nodraw_bbox, nodraw_rbbox=args.nodraw_rbbox, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'seg_filter':
                try:
                    proc = seg_filter.SegFilter(logger, logits_th=args.logits_th, classes=args.classes, labels=args.labels,
                                                nodraw=args.nodraw, del_logits=args.del_logits)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'showimg':
                try:
                    proc = showimg.Showimg(logger, host=args.host, port=args.port, password=args.password, svname=args.svname, maxrecsize=args.maxrecsize)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.timeout, args.format, tm,
                                       None, None, output_image_file=None)
                if code != 0:
                    return code, ret

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'redis':
            rd = redis.Redis(logger=logger, wsl_name=args.wsl_name, wsl_user=args.wsl_user)
            if args.cmd == 'docker_run':
                ret = rd.docker_run(args.port, args.password)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

            elif args.cmd == 'docker_stop':
                ret = rd.docker_stop()
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'install':
            self.inst = install.Install(logger=logger, wsl_name=args.wsl_name, wsl_user=args.wsl_user)
            if args.cmd == 'redis':
                ret = self.inst.redis()
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'server':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.server(Path(args.data), args.install_iinfer,
                                       install_onnx=args.install_onnx,
                                       install_mmdet=args.install_mmdet,
                                       install_mmseg=args.install_mmseg,
                                       install_mmcls=args.install_mmcls,
                                       install_mmpretrain=args.install_mmpretrain,
                                       install_insightface=args.install_insightface,
                                       install_from=args.install_from,
                                       install_no_python=args.install_no_python,
                                       install_tag=args.install_tag, install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'onnx':
                ret = self.inst.onnx(install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'mmdet':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.mmdet(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'mmseg':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.mmseg(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'mmcls':
                ret = self.inst.mmcls(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'mmpretrain':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.mmpretrain(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'insightface':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.insightface(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        else:
            msg = {"warn":f"Unkown mode."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg

        return 0, ret
