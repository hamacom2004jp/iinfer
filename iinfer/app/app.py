from iinfer import version
from iinfer.app import common
from iinfer.app import client
from iinfer.app import gui
from iinfer.app import install
from iinfer.app import postprocess
from iinfer.app import redis
from iinfer.app import server
from iinfer.app.postprocesses import csv
from iinfer.app.postprocesses import det_filter
from iinfer.app.postprocesses import det_jadge
from iinfer.app.postprocesses import cls_jadge
from iinfer.app.postprocesses import httpreq
from pathlib import Path
import argparse
import argcomplete
import os
import sys
import time


def main(args_list:list=None):
    return _main(args_list)

def _main(args_list:list=None):
    """
    コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
    """
    parser = argparse.ArgumentParser(prog='iinfer', description='This application generates modules to set up the application system.')
    parser.add_argument('--version', help='show version infomation.', action='store_true')
    parser.add_argument('--host', help='Setting the redis server host.', default=os.environ.get('REDIS_HOST', 'localhost'))
    parser.add_argument('--port', help='Setting the redis server port.', type=int, default=int(os.environ.get('REDIS_PORT', '6379')))
    parser.add_argument('--password', help='Setting the redis server password.', default=os.environ.get('REDIS_PASSWORD', 'password'))
    parser.add_argument('--svname', help='Setting the service name of server.', type=str, default='server')
    parser.add_argument('-u', '--useopt', help=f'Use options file.')
    parser.add_argument('-s', '--saveopt', help=f'save options file. with --useopt option.', action='store_true')
    parser.add_argument('-f', '--format', help='Setting the cmd format.', action='store_true')
    parser.add_argument('-m', '--mode', help='Setting the boot mode.', choices=['redis', 'install', 'server', 'client', 'postprocess', 'gui'])
    parser.add_argument('--data', help='Setting the data directory.', default=common.HOME_DIR / ".iinfer")
    parser.add_argument('-n', '--name', help='Setting the cmd name.')
    parser.add_argument('--timeout', help='Setting the cmd timeout.', type=int, default=60)
    parser.add_argument('-c', '--cmd', help='Setting the cmd type.',
                        choices=['redis', 'server', 'onnx', 'mmdet', 'mmcls', 'mmpretrain', # install mode
                                 'docker_run', 'docker_stop', # redis mode
                                 'start', 'stop', # server or client or gui mode
                                 'list' , # server mode
                                 'deploy', 'deploy_list', 'undeploy', 'predict', 'predict_type_list', 'capture', # client mode
                                 'det_filter', 'det_jadge', 'cls_jadge', 'csv', 'httpreq', # postprocess mode
                                ])
    parser.add_argument('-T','--use_track', help='Setting the multi object tracking enable for Object Detection.', action='store_true')
    parser.add_argument('--model_img_width', help='Setting the cmd deploy model_img_width.', type=int)
    parser.add_argument('--model_img_height', help='Setting the cmd deploy model_img_height.', type=int)
    parser.add_argument('--model_file', help='Setting the cmd deploy model_file file.')
    parser.add_argument('--model_conf_file', help='Setting the cmd deploy model_conf_file file.', action='append')
    parser.add_argument('--predict_type', help='Setting the cmd deploy predict_type. If Custom, custom_predict_py must be specified.',
                        choices=['Custom'] + list(common.BASE_MODELS.keys()))
    parser.add_argument('--custom_predict_py', help='Setting the cmd deploy custom_predict.py file.')
    parser.add_argument('--label_file', help='Setting the cmd deploy label_txt file.')
    parser.add_argument('--color_file', help='Setting the cmd deploy color_txt file.')
    parser.add_argument('--overwrite', help='Setting the cmd deploy overwrite save.', action='store_true')

    parser.add_argument('--model_provider', help='Setting the cmd start model_provider.',
                        choices=['CPUExecutionProvider','CUDAExecutionProvider','TensorrtExecutionProvider'], default='CPUExecutionProvider')
    parser.add_argument('--gpuid', help='Setting the cmd start gpuid.', type=int, default=None)
    parser.add_argument('-i', '--input_file', help='Setting the cmd input file.', default=None)
    parser.add_argument('-o', '--output_file', help='Setting the cmd output file.', default=None)
    parser.add_argument('-P', '--output_preview', help='Setting the output preview.', action='store_true')
    parser.add_argument('--stdin', help='Setting the cmd stdin.', action='store_true')
    parser.add_argument('--nodraw', help='Setting the cmd predict nodraw.', action='store_true')
    parser.add_argument('--image_type', help='Setting the cmd predict image type.', choices=['bmp', 'png', 'jpeg', 'capture'], default='jpeg')
    parser.add_argument('--wsl_name', help='WSL distribution name.')
    parser.add_argument('--wsl_user', help='WSL distribution user.')
    parser.add_argument('-d', '--capture_device', help='Setting the capture input device. device id, video file, rtsp url.', default='0')
    parser.add_argument('--capture_frame_width', help='Setting the capture input frame width.', type=int, default=None)
    parser.add_argument('--capture_frame_height', help='Setting the capture input frame height.', type=int, default=None)
    parser.add_argument('--capture_fps', help='Setting the capture input fps.', type=int, default=1000)
    parser.add_argument('--capture_count', help='Setting the capture count.', type=int, default=-1)

    parser.add_argument('--fileup_name', help='Setting the param name of file upload.', type=str, default='file')
    parser.add_argument('--img_connectstr', help='Setting the postprocess img_connectstr.', type=str, default=None)
    parser.add_argument('--json_connectstr', help='Setting the postprocess json_connectstr.', type=str, default=None)
    parser.add_argument('--text_connectstr', help='Setting the postprocess text_connectstr.', type=str, default=None)

    parser.add_argument('--out_headers', help='Setting the csv cmd out_headers in postprocess.', type=str, action='append')
    parser.add_argument('--noheader', help='Setting the csv cmd noheader in postprocess.', action='store_true')

    parser.add_argument('--score_th', help='Setting the postprocess score_th.', type=float, default=0.0)
    parser.add_argument('--width_th', help='Setting the postprocess width_th.', type=int, default=0)
    parser.add_argument('--height_th', help='Setting the postprocess height_th.', type=int, default=0)
    parser.add_argument('--classes', help='Setting the postprocess classes.', type=int, action='append')
    parser.add_argument('--labels', help='Setting the postprocess labels.', type=str, action='append')
    parser.add_argument('--ok_score_th', help='Setting the postprocess ok_score_th.', type=float, default=None)
    parser.add_argument('--ok_classes', help='Setting the postprocess ok_classes.', type=int, action='append')
    parser.add_argument('--ok_labels', help='Setting the postprocess ok_labels.', type=str, action='append')
    parser.add_argument('--ng_score_th', help='Setting the postprocess ng_score_th.', type=float, default=None)
    parser.add_argument('--ng_classes', help='Setting the postprocess ng_classes.', type=int, action='append')
    parser.add_argument('--ng_labels', help='Setting the postprocess ng_labels.', type=str, action='append')
    parser.add_argument('--ext_score_th', help='Setting the postprocess ext_score_th.', type=float, default=None)
    parser.add_argument('--ext_classes', help='Setting the postprocess ext_classes.', type=int, action='append')
    parser.add_argument('--ext_labels', help='Setting the postprocess ext_labels.', type=str, action='append')

    argcomplete.autocomplete(parser)
    if args_list is not None:
        args = parser.parse_args(args=args_list)
    else:
        args = parser.parse_args()
    args_dict = vars(args)
    opt = common.loadopt(args.useopt)
    host = common.getopt(opt, 'host', preval=args_dict, withset=True)
    port = common.getopt(opt, 'port', preval=args_dict, withset=True)
    password = common.getopt(opt, 'password', preval=args_dict, withset=True)
    svname = common.getopt(opt, 'svname', preval=args_dict, withset=True)
    format = common.getopt(opt, 'format', preval=args_dict, withset=True)
    mode = common.getopt(opt, 'mode', preval=args_dict, withset=True)
    data = common.getopt(opt, 'data', preval=args_dict, withset=True)
    timeout = common.getopt(opt, 'timeout', preval=args_dict, withset=True)
    name = common.getopt(opt, 'name', preval=args_dict, withset=True)
    cmd = common.getopt(opt, 'cmd', preval=args_dict, withset=True)
    model_img_width = common.getopt(opt, 'model_img_width', preval=args_dict, withset=True)
    model_img_height = common.getopt(opt, 'model_img_height', preval=args_dict, withset=True)
    model_file = common.getopt(opt, 'model_file', preval=args_dict, withset=True)
    model_conf_file = common.getopt(opt, 'model_conf_file', preval=args_dict, withset=True)
    predict_type = common.getopt(opt, 'predict_type', preval=args_dict, withset=True)
    custom_predict_py = common.getopt(opt, 'custom_predict_py', preval=args_dict, withset=True)
    label_file = common.getopt(opt, 'label_file', preval=args_dict, withset=True)
    color_file = common.getopt(opt, 'color_file', preval=args_dict, withset=True)
    overwrite = common.getopt(opt, 'overwrite', preval=args_dict, withset=True)

    model_provider = common.getopt(opt, 'model_provider', preval=args_dict, withset=True)
    gpuid = common.getopt(opt, 'gpuid', preval=args_dict, withset=True)
    input_file = common.getopt(opt, 'input_file', preval=args_dict, withset=True)
    output_file = common.getopt(opt, 'output_file', preval=args_dict, withset=True)
    output_preview = common.getopt(opt, 'output_preview', preval=args_dict, withset=True)
    stdin = common.getopt(opt, 'stdin', preval=args_dict, withset=True)
    nodraw = common.getopt(opt, 'nodraw', preval=args_dict, withset=True)
    image_type = common.getopt(opt, 'image_type', preval=args_dict, withset=True)
    use_track = common.getopt(opt, 'use_track', preval=args_dict, withset=True)

    wsl_name = common.getopt(opt, 'wsl_name', preval=args_dict, withset=True)
    wsl_user = common.getopt(opt, 'wsl_user', preval=args_dict, withset=True)

    capture_device = common.getopt(opt, 'capture_device', preval=args_dict, withset=True)
    capture_frame_width = common.getopt(opt, 'capture_frame_width', preval=args_dict, withset=True)
    capture_frame_height = common.getopt(opt, 'capture_frame_height', preval=args_dict, withset=True)
    capture_fps = common.getopt(opt, 'capture_fps', preval=args_dict, withset=True)
    capture_count = common.getopt(opt, 'capture_count', preval=args_dict, withset=True)

    json_connectstr = common.getopt(opt, 'json_connectstr', preval=args_dict, withset=True)
    img_connectstr = common.getopt(opt, 'img_connectstr', preval=args_dict, withset=True)
    text_connectstr = common.getopt(opt, 'text_connectstr', preval=args_dict, withset=True)
    fileup_name = common.getopt(opt, 'fileup_name', preval=args_dict, withset=True)

    out_headers = common.getopt(opt, 'out_headers', preval=args_dict, withset=True)
    noheader = common.getopt(opt, 'noheader', preval=args_dict, withset=True)

    score_th = common.getopt(opt, 'score_th', preval=args_dict, withset=True)
    width_th = common.getopt(opt, 'width_th', preval=args_dict, withset=True)
    height_th = common.getopt(opt, 'height_th', preval=args_dict, withset=True)
    classes = common.getopt(opt, 'classes', preval=args_dict, withset=True)
    labels = common.getopt(opt, 'labels', preval=args_dict, withset=True)

    ok_score_th = common.getopt(opt, 'ok_score_th', preval=args_dict, withset=True)
    ok_classes = common.getopt(opt, 'ok_classes', preval=args_dict, withset=True)
    ok_labels = common.getopt(opt, 'ok_labels', preval=args_dict, withset=True)
    ng_score_th = common.getopt(opt, 'ng_score_th', preval=args_dict, withset=True)
    ng_classes = common.getopt(opt, 'ng_classes', preval=args_dict, withset=True)
    ng_labels = common.getopt(opt, 'ng_labels', preval=args_dict, withset=True)
    ext_score_th = common.getopt(opt, 'ext_score_th', preval=args_dict, withset=True)
    ext_classes = common.getopt(opt, 'ext_classes', preval=args_dict, withset=True)
    ext_labels = common.getopt(opt, 'ext_labels', preval=args_dict, withset=True)

    tm = time.time()
    ret = {"success":f"Start command. {args}"}

    if args.saveopt:
        if args.useopt is None:
            msg = {"warn":f"Please specify the --useopt option."}
            common.print_format(msg, format, tm)
            return 1, msg
        common.saveopt(opt, args.useopt)
        ret = {"success":f"Save options file. {args.useopt}"}

    if args.version:
        common.print_format(version.__description__, False, tm)
        return 0, version.__description__
    elif mode == 'server':
        logger, _ = common.load_config(mode)
        if cmd == 'start':
            if data is None:
                msg = {"warn":f"Please specify the --data option."}
                common.print_format(msg, format, tm)
                return 1, msg
            if svname is None:
                msg = {"warn":f"Please specify the --svname option."}
                common.print_format(msg, format, tm)
                return 1, msg
            sv = server.Server(Path(data), logger, redis_host=host, redis_port=port, redis_password=password, svname=svname)
            sv.start_server()
        elif cmd == 'stop':
            if svname is None:
                msg = {"warn":f"Please specify the --svname option."}
                common.print_format(msg, format, tm)
                return 1, msg
            cl = client.Client(logger, redis_host=host, redis_port=port, redis_password=password, svname=svname)
            ret = cl.stop_server(timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret
        elif cmd == 'list':
            sv = server.Server(Path(data), logger, redis_host=host, redis_port=port, redis_password=password, svname='server') # list取得なのでデフォルトのsvnameを指定
            ret = sv.list_server()
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret
        else:
            msg = {"warn":f"Unkown command."}
            common.print_format(msg, format, tm)
            return 1, msg

    elif mode == 'gui':
        logger, _ = common.load_config(mode)
        if cmd == 'start':
            if data is None:
                msg = {"warn":f"Please specify the --data option."}
                common.print_format(msg, format, tm)
                return 1, msg
            web = gui.Web(logger, Path(data))
            web.start()
            msg = {"success":"eel web complate."}
            common.print_format(msg, format, tm)
            return 0, msg
        else:
            msg = {"warn":f"Unkown command."}
            common.print_format(msg, format, tm)
            return 1, msg

    elif mode == 'client':
        logger, _ = common.load_config(mode)
        if svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, format, tm)
            return 1, msg
        cl = client.Client(logger, redis_host=host, redis_port=port, redis_password=password, svname=svname)
        if cmd == 'deploy':
            model_file = Path(model_file) if model_file is not None else None
            if model_conf_file is not None:
                model_conf_file = [Path(f) for f in model_conf_file if f is not None and f != '']
            custom_predict_py = Path(custom_predict_py) if custom_predict_py is not None else None
            label_file = Path(label_file) if label_file is not None else None
            color_file = Path(color_file) if color_file is not None else None
            ret = cl.deploy(name, model_img_width, model_img_height, model_file, model_conf_file, predict_type, custom_predict_py,
                            label_file=label_file, color_file=color_file, overwrite=overwrite, timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'deploy_list':
            ret = cl.deploy_list(timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'undeploy':
            ret = cl.undeploy(name, timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'start':
            ret = cl.start(name, model_provider=model_provider, use_track=use_track, gpuid=gpuid, timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'stop':
            ret = cl.stop(name, timeout=timeout)
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'predict':
            if input_file is not None:
                ret = cl.predict(name, image_file=Path(input_file), image_type=image_type, output_image_file=output_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                if type(ret) is list:
                    for r in ret:
                        common.print_format(r, format, tm)
                else:
                    common.print_format(ret, format, tm)
            elif stdin:
                if image_type is None:
                    msg = {"warn":f"Please specify the --image_type option."}
                    common.print_format(msg, format, tm)
                    return 1, msg
                if image_type == 'capture':
                    for line in sys.stdin:
                        ret = cl.predict(name, image=line, image_type=image_type, output_image_file=output_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                        common.print_format(ret, format, tm)
                        tm = time.time()
                else:
                    ret = cl.predict(name, image=sys.stdin.buffer.read(), image_type=image_type, output_image_file=output_file, output_preview=output_preview, nodraw=nodraw, timeout=timeout)
                    common.print_format(ret, format, tm)
                    tm = time.time()
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg

        elif cmd == 'predict_type_list':
            type_list = [dict(predict_type=key, site=val['site'], image_width=val['image_width'], image_height=val['image_height'], use_model_conf=val['use_model_conf']) for key,val in common.BASE_MODELS.items()]
            type_list.append(dict(predict_type='Custom', site='Custom', image_width=None, image_height=None))
            common.print_format(type_list, format, tm)
            ret = type_list

        #elif cmd == 'capture_predict':
        #    for ret in cl.capture_predict(name, output_image_file=output_image_file, timeout=timeout,
        #                         capture_device=capture_device, capture_frame_width=capture_frame_width, capture_frame_height=capture_frame_height,
        #                         capture_fps=capture_fps, capture_output_fps=capture_output_fps,
        #                         output_preview=output_preview):
        #        common.print_format(ret, format, tm)
        #        tm = time.time()

        elif cmd == 'capture':
            count = 0
            for t,b64,h,w,c in cl.capture(capture_device=capture_device, image_type=image_type,
                                 capture_frame_width=capture_frame_width, capture_frame_height=capture_frame_height, capture_fps=capture_fps,
                                 output_preview=output_preview):
                ret = f"{t},"+b64+f",{h},{w},{c}"
                common.print_format(ret, False, tm)
                tm = time.time()
                count += 1
                if capture_count > 0 and count >= capture_count:
                    break

        else:
            msg = {"warn":f"Unkown command."}
            common.print_format(msg, format, tm)
            return 1, msg

    elif mode == 'postprocess':
        logger, _ = common.load_config(mode)
        def _to_proc(f, proc:postprocess.Postprocess, json_connectstr, img_connectstr, text_connectstr, timeout, format, tm):
            for line in f:
                line = line.rstrip()
                if line == "":
                    continue
                try:
                    json_session, img_session, text_session = proc.create_session(json_connectstr, img_connectstr, text_connectstr)
                    ret = proc.postprocess(json_session, img_session, text_session, line, timeout=timeout)
                    common.print_format(ret, format, tm)
                except Exception as e:
                    msg = {"warn":f"Invalid input. {e}"}
                    common.print_format(msg, format, tm)
                    ret = msg
                tm = time.time()
            return ret

        if cmd == 'det_filter':
            proc = det_filter.DetFilter(logger, score_th=score_th, width_th=width_th, height_th=height_th, classes=classes, labels=labels, nodraw=nodraw, output_preview=output_preview)
            if input_file is not None:
                with open(input_file, 'r', encoding="UTF-8") as f:
                    ret = _to_proc(f, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            elif stdin:
                ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg

        elif cmd == 'det_jadge':
            try:
                proc = det_jadge.DetJadge(logger, ok_score_th=ok_score_th, ok_classes=ok_classes, ok_labels=ok_labels,
                                        ng_score_th=ng_score_th, ng_classes=ng_classes, ng_labels=ng_labels,
                                        ext_score_th=ext_score_th, ext_classes=ext_classes, ext_labels=ext_labels,
                                        nodraw=nodraw, output_preview=output_preview)
            except Exception as e:
                msg = {"warn":f"Invalid options. {e}"}
                common.print_format(msg, format, tm)
                return 1, msg
            if input_file is not None:
                with open(input_file, 'r', encoding="UTF-8") as f:
                    ret = _to_proc(f, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            elif stdin:
                ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg

        elif cmd == 'cls_jadge':
            proc = cls_jadge.ClaJadge(logger, ok_score_th=ok_score_th, ok_classes=ok_classes, ok_labels=ok_labels,
                                      ng_score_th=ng_score_th, ng_classes=ng_classes, ng_labels=ng_labels,
                                      ext_score_th=ext_score_th, ext_classes=ext_classes, ext_labels=ext_labels,
                                      nodraw=nodraw, output_preview=output_preview)
            if input_file is not None:
                with open(input_file, 'r', encoding="UTF-8") as f:
                    ret = _to_proc(f, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            elif stdin:
                ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, None, timeout, format, tm)
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg

        elif cmd == 'csv':
            proc = csv.Csv(logger, out_headers=out_headers, noheader=noheader)
            if input_file is not None:
                with open(input_file, 'r') as f:
                    ret = _to_proc(f, proc, json_connectstr, img_connectstr, None, timeout, False, tm)
            elif stdin:
                ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, None, timeout, False, tm)
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg

        elif cmd == 'httpreq':
            proc = httpreq.Httpreq(logger, fileup_name=fileup_name)
            if input_file is not None:
                with open(input_file, 'r') as f:
                    ret = _to_proc(f, proc, json_connectstr, img_connectstr, text_connectstr, timeout, format, tm)
            elif stdin:
                ret = _to_proc(sys.stdin, proc, json_connectstr, img_connectstr, text_connectstr, timeout, format, tm)
            else:
                msg = {"warn":f"Image file or stdin is empty."}
                common.print_format(msg, format, tm)
                return 1, msg
        else:
            msg = {"warn":f"Unkown command."}
            common.print_format(msg, format, tm)
            return 1, msg

    elif mode == 'redis':
        logger, _ = common.load_config(mode)
        rd = redis.Redis(logger=logger, wsl_name=wsl_name, wsl_user=wsl_user)
        if cmd == 'docker_run':
            ret = rd.docker_run(port, password)
            common.print_format(ret, format, tm)

        elif cmd == 'docker_stop':
            ret = rd.docker_stop()
            common.print_format(ret, format, tm)

        else:
            msg = {"warn":f"Unkown command."}
            common.print_format(msg, format, tm)
            return 1, msg

    elif mode == 'install':
        logger, _ = common.load_config(mode)
        inst = install.Install(logger=logger)
        if cmd == 'redis':
            ret = inst.redis()
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'server':
            ret = inst.server()
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'onnx':
            ret = inst.onnx()
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'mmdet':
            if data is None:
                msg = {"warn":f"Please specify the --data option."}
                common.print_format(msg, format, tm)
                return 1, msg
            ret = inst.mmdet(Path(data))
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'mmcls':
            ret = inst.mmcls()
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

        elif cmd == 'mmpretrain':
            if data is None:
                msg = {"warn":f"Please specify the --data option."}
                common.print_format(msg, format, tm)
                return 1, msg
            ret = inst.mmpretrain(Path(data))
            common.print_format(ret, format, tm)
            if 'success' not in ret:
                return 1, ret

    else:
        msg = {"warn":f"Unkown mode."}
        common.print_format(msg, format, tm)
        return 1, msg

    return 0, ret
