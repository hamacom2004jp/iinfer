from iinfer import version
from iinfer.app import common, client, gui, install, options, postprocess, redis, server, web
from iinfer.app.postprocesses import cls_jadge, csv, det_clip, det_face_store, det_filter, det_jadge, httpreq, seg_bbox, seg_filter
from pathlib import Path
import argparse
import argcomplete
import cv2
import os
import sys
import time


def main(args_list:list=None):
    app = IinferApp()
    return app.main(args_list)[0]

class IinferApp:
    def __init__(self):
        self.sv = None
        self.cl = None
        self.web = None
        common.copy_sample()

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
            common.print_format(version.__description__, False, tm, None, False)
            return 0, version.__description__
        elif args.mode == 'server':
            logger, _ = common.load_config(args.mode)
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
                self.sv.start_server()
            elif args.cmd == 'stop':
                if args.svname is None:
                    msg = {"warn":f"Please specify the --svname option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                ret = cl.stop_server(timeout=args.timeout)
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
            logger, _ = common.load_config(args.mode)
            if args.cmd == 'start':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                self.web = gui.Gui(logger, Path(args.data))
                self.web.start()
                msg = {"success":"eel web complate."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 0, msg
            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'web':
            logger, _ = common.load_config(args.mode)
            if args.cmd == 'start':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                self.web = web.Web(logger, Path(args.data))
                self.web.start(args.allow_host, args.listen_port)
                msg = {"success":"web complate."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 0, msg
            elif args.cmd == 'stop':
                self.web = web.Web(logger, Path(args.data))
                self.web.stop()
                msg = {"success":"web complate."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 0, msg
            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg
            
        elif args.mode == 'client':
            logger, _ = common.load_config(args.mode)
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
                ret = self.cl.deploy(args.name, args.model_img_width, args.model_img_height, args.model_file, args.model_conf_file, args.predict_type,
                                args.custom_predict_py, label_file=args.label_file, color_file=args.color_file,
                                before_injection_conf=args.before_injection_conf, before_injection_type=args.before_injection_type, before_injection_py=args.before_injection_py,
                                after_injection_conf=args.after_injection_conf, after_injection_type=args.after_injection_type, after_injection_py=args.after_injection_py,
                                overwrite=args.overwrite, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'deploy_list':
                ret = self.cl.deploy_list(timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'undeploy':
                ret = self.cl.undeploy(args.name, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'start':
                ret = self.cl.start(args.name, model_provider=args.model_provider, use_track=args.use_track, gpuid=args.gpuid, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'stop':
                ret = self.cl.stop(args.name, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'predict':
                try:
                    if args.input_file is not None:
                        ret = self.cl.predict(args.name, image_file=args.input_file, pred_input_type=args.pred_input_type,
                                                output_image_file=args.output_image, output_preview=args.output_preview,
                                                nodraw=args.nodraw, timeout=args.timeout)
                        if type(ret) is list:
                            for r in ret:
                                common.print_format(r, args.format, tm, args.output_json, args.output_json_append)
                                tm = time.perf_counter()
                                args.output_json_append = True
                        else:
                            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                    elif args.stdin:
                        if args.pred_input_type is None:
                            msg = {"warn":f"Please specify the --pred_input_type option."}
                            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                            return 1, msg
                        if args.pred_input_type in ['capture', 'prompt']:
                            for line in sys.stdin:
                                ret = self.cl.predict(args.name, image=line, pred_input_type=args.pred_input_type,
                                                      output_image_file=args.output_image, output_preview=args.output_preview,
                                                      nodraw=args.nodraw, timeout=args.timeout)
                                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                                tm = time.perf_counter()
                                args.output_json_append = True
                        else:
                            ret = self.cl.predict(args.name, image=sys.stdin.buffer.read(), pred_input_type=args.pred_input_type,
                                                  output_image_file=args.output_image, output_preview=args.output_preview,
                                                  nodraw=args.nodraw, timeout=args.timeout)
                            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                            tm = time.perf_counter()
                    else:
                        msg = {"warn":f"Image file or stdin is empty."}
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                        return 1, msg
                finally:
                    try:
                        cv2.destroyWindow('preview')
                    except:
                        pass

            elif args.cmd == 'file_list':
                ret = self.cl.file_list(args.svpath, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_mkdir':
                ret = self.cl.file_mkdir(args.svpath, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_rmdir':
                ret = self.cl.file_rmdir(args.svpath, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_download':
                download_file = Path(download_file) if download_file is not None else None
                ret = self.cl.file_download(args.svpath, download_file, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret
            
            elif args.cmd == 'file_upload':
                upload_file = Path(upload_file) if upload_file is not None else None
                ret = self.cl.file_upload(args.svpath, upload_file, timeout=args.timeout)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'file_remove':
                ret = self.cl.file_remove(args.svpath, timeout=args.timeout)
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

            elif args.cmd == 'prompt':
                count = 0
                append = False
                try:
                    for t,b64,fn in self.cl.prompt(prompt_format=args.prompt_format, prompt_form=args.prompt_form):
                        ret = f"{t},"+b64+f",{fn}"
                        if args.output_csv is not None:
                            with open(args.output_csv, 'a' if append else 'w', encoding="utf-8") as f:
                                print(ret, file=f)
                                append = True
                        else: common.print_format(ret, False, tm, None, False)
                        tm = time.perf_counter()
                        count += 1
                        if args.prompt_count > 0 and count >= args.prompt_count:
                            break
                finally:
                    pass

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'postprocess':
            logger, _ = common.load_config(args.mode)
            def _to_proc(f, proc:postprocess.Postprocess, json_connectstr, img_connectstr, text_connectstr, timeout,
                         format, tm, output_json, output_json_append, output_image_file=None, output_csv=None):
                try:
                    for line in f:
                        line = line.rstrip()
                        if line == "":
                            continue
                        try:
                            json_session, img_session, text_session = proc.create_session(json_connectstr, img_connectstr, text_connectstr)
                            ret = proc.postprocess(json_session, img_session, text_session, line, output_image_file=output_image_file, timeout=timeout)
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

            def _exec_proc(input_file, stdin, proc:postprocess.Postprocess, json_connectstr, img_connectstr, text_connectstr, timeout,
                           format, tm, output_json, output_json_append, output_image_file=None, output_csv=None):
                if input_file is not None:
                    with open(input_file, 'r', encoding="UTF-8") as f:
                        ret = _to_proc(f, proc, json_connectstr, img_connectstr, None, timeout, format, tm, output_json, output_json_append,
                                       output_image_file=output_image_file, output_csv=output_csv)
                elif stdin:
                    ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, None, timeout, format, tm, output_json, output_json_append,
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
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       args.format, tm, args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'csv':
                try:
                    proc = csv.Csv(logger, out_headers=args.out_headers, noheader=args.noheader)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       False, tm, None, False, output_image_file=None, output_csv=args.output_csv)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_clip':
                try:
                    proc = det_clip.DetClip(logger, image_type=args.image_type, clip_margin=args.clip_margin)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       False, tm, None, False, output_image_file=None, output_csv=args.output_csv)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_face_store':
                try:
                    proc = det_face_store.DetFaceStore(logger, face_threshold=args.face_threshold, image_type=args.image_type,
                                                       clip_margin=args.clip_margin)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       False, tm, args.output_json, args.output_json_append, output_image_file=None)
                if code != 0:
                    return code, ret

            elif args.cmd == 'det_filter':
                try:
                    proc = det_filter.DetFilter(logger, score_th=args.score_th, width_th=args.width_th, height_th=args.height_th,
                                                classes=args.classes, labels=args.labels, nodraw=args.nodraw, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       args.format, tm, args.output_json, args.output_json_append, output_image_file=args.output_image)
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
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       args.format, tm, args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'httpreq':
                try:
                    proc = httpreq.Httpreq(logger, fileup_name=args.fileup_name)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, args.text_connectstr,
                                       args.timeout, args.format, tm, None, False, output_image_file=None)
                if code != 0:
                    return code, ret

            elif args.cmd == 'seg_bbox':
                try:
                    proc = seg_bbox.SegBBox(logger, del_segments=args.del_segments, nodraw=args.nodraw,
                                            nodraw_bbox=args.nodraw_bbox, nodraw_rbbox=args.nodraw_rbbox, output_preview=args.output_preview)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       args.format, tm, args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            elif args.cmd == 'seg_filter':
                try:
                    proc = seg_filter.SegFilter(logger, logits_th=args.logits_th, classes=args.classes, labels=args.labels,
                                                nodraw=args.nodraw, del_logits=args.del_logits)
                except Exception as e:
                    common.print_format({"warn":f"Invalid options. {e}"}, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                code, ret = _exec_proc(args.input_file, args.stdin, proc, args.json_connectstr, args.img_connectstr, None, args.timeout,
                                       args.format, tm, args.output_json, args.output_json_append, output_image_file=args.output_image)
                if code != 0:
                    return code, ret

            else:
                msg = {"warn":f"Unkown command."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg

        elif args.mode == 'redis':
            logger, _ = common.load_config(args.mode)
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
            logger, _ = common.load_config(args.mode)
            self.inst = install.Install(logger=logger)
            if args.cmd == 'redis':
                ret = self.inst.redis()
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'server':
                install_set = not (args.install_onnx or args.install_mmdet or args.install_mmseg or args.install_mmcls or \
                                   args.install_mmpretrain or args.install_insightface or args.install_diffusers or args.install_llamaindex)
                onnx = install_set
                mmdet = install_set
                mmseg = install_set
                mmcls = False
                mmpretrain = install_set
                insightface = False
                diffusers = install_set
                llamaindex = install_set
                onnx = args.install_onnx if args.install_onnx else onnx
                mmdet = args.install_mmdet if args.install_mmdet else mmdet
                mmseg = args.install_mmseg if args.install_mmseg else mmseg
                mmcls = args.install_mmcls if args.install_mmcls else mmcls
                mmpretrain = args.install_mmpretrain if args.install_mmpretrain else mmpretrain
                insightface = args.install_insightface if args.install_insightface else insightface
                diffusers = args.install_diffusers if args.install_diffusers else diffusers
                llamaindex = args.install_llamaindex if args.install_llamaindex else llamaindex
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.server(Path(args.data), args.install_iinfer, install_onnx=onnx,
                                install_mmdet=mmdet, install_mmseg=mmseg, install_mmcls=mmcls, install_mmpretrain=mmpretrain,
                                install_insightface=insightface, install_diffusers=diffusers, install_llamaindex=llamaindex,
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
            
            elif args.cmd == 'diffusers':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.diffusers(Path(args.data), install_use_gpu=args.install_use_gpu)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append)
                if 'success' not in ret:
                    return 1, ret

            elif args.cmd == 'llamaindex':
                if args.data is None:
                    msg = {"warn":f"Please specify the --data option."}
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                    return 1, msg
                ret = self.inst.llamaindex(Path(args.data), install_use_gpu=args.install_use_gpu)
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
