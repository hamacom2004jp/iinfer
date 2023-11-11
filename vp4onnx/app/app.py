from vp4onnx.app import common
from vp4onnx.app import client
from vp4onnx.app import server
from pathlib import Path
import argparse
import sys
import time


def main(HOME_DIR:str):
    """
    コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。

    Args:
        data_dir (Path): データディレクトリのパス
    """
    parser = argparse.ArgumentParser(
        prog='python -m vp4onnx',
        description='This application generates modules to set up the application system.')
    parser.add_argument('--host', help='Setting the redis server host.', default='localhost')
    parser.add_argument('--port', help='Setting the redis server port.', type=int, default=6379)
    parser.add_argument('-p', '--password', help='Setting the redis server password.')
    parser.add_argument('-u', '--useopt', help=f'Use options file.')
    parser.add_argument('-s', '--saveopt', help=f'save options file. with --useopt option.', action='store_true')
    parser.add_argument('-f', '--format', help='Setting the cmd format.', action='store_true')
    parser.add_argument('-m', '--mode', help='Setting the boot mode.', choices=['server', 'client'])
    parser.add_argument('--data', help='Setting the data directory.', default=Path(HOME_DIR) / ".vp4onnx")
    parser.add_argument('-n', '--name', help='Setting the cmd name.')
    parser.add_argument('--timeout', help='Setting the cmd timeout.', type=int, default=15)
    parser.add_argument('-c', '--cmd', help='Setting the cmd type.', choices=['deploy', 'deploy_list', 'undeploy', 'start', 'stop', 'predict', 'predict_type_list'])
    #parser.add_argument('--redis', help='Commands to operate the redis container.', choices=['docker_run', 'docker_stop'])
    parser.add_argument('--model_img_width', help='Setting the cmd deploy model_img_width.', type=int)
    parser.add_argument('--model_img_height', help='Setting the cmd deploy model_img_height.', type=int)
    parser.add_argument('--model_onnx', help='Setting the cmd deploy model_onnx file.')
    parser.add_argument('--predict_type', help='Setting the cmd deploy predict_type. If Custom, custom_predict_py must be specified.',
                        choices=['Custom'] + list(common.BASE_MODELS.keys()))
    parser.add_argument('--custom_predict_py', help='Setting the cmd deploy custom_predict.py file.')
    parser.add_argument('--model_provider', help='Setting the cmd start model_provider.',
                        choices=['CPUExecutionProvider','CUDAExecutionProvider','TensorrtExecutionProvider'], default='CPUExecutionProvider')
    parser.add_argument('-i', '--image_file', help='Setting the cmd predict image file.', default=None)
    parser.add_argument('-o', '--output_image_file', help='Setting the cmd predict output image file.', default=None)
    parser.add_argument('--image_stdin', help='Setting the cmd predict image for stdin.', action='store_true')

    args = parser.parse_args()
    args_dict = vars(args)
    opt = common.loadopt(args.useopt)
    host = common.getopt(opt, 'host', preval=args_dict, withset=True)
    port = common.getopt(opt, 'port', preval=args_dict, withset=True)
    password = common.getopt(opt, 'password', preval=args_dict, withset=True)
    format = common.getopt(opt, 'format', preval=args_dict, withset=True)
    mode = common.getopt(opt, 'mode', preval=args_dict, withset=True)
    data = common.getopt(opt, 'data', preval=args_dict, withset=True)
    timeout = common.getopt(opt, 'timeout', preval=args_dict, withset=True)
    name = common.getopt(opt, 'name', preval=args_dict, withset=True)
    cmd = common.getopt(opt, 'cmd', preval=args_dict, withset=True)
    model_img_width = common.getopt(opt, 'model_img_width', preval=args_dict, withset=True)
    model_img_height = common.getopt(opt, 'model_img_height', preval=args_dict, withset=True)
    model_onnx = common.getopt(opt, 'model_onnx', preval=args_dict, withset=True)
    predict_type = common.getopt(opt, 'predict_type', preval=args_dict, withset=True)
    custom_predict_py = common.getopt(opt, 'custom_predict_py', preval=args_dict, withset=True)
    model_provider = common.getopt(opt, 'model_provider', preval=timeout, withset=True)
    image_file = common.getopt(opt, 'image_file', preval=args_dict, withset=True)
    output_image_file = common.getopt(opt, 'output_image_file', preval=args_dict, withset=True)
    image_stdin = common.getopt(opt, 'image_stdin', preval=args_dict, withset=True)
    redis = common.getopt(opt, 'redis', preval=args_dict, withset=True)
    tm = time.time()

    if args.saveopt:
        if args.useopt is None:
            common.print_format({"warn":f"Please specify the --useopt option."}, format, tm)
            exit(1)
        common.saveopt(opt, args.useopt)

    logger_client, logger_server, config = common.load_config()
    if mode == 'server':
        if data is None:
            parser.print_help()
            exit(1)
        sv = server.Server(Path(data), logger_server, redis_host=host, redis_port=port, redis_password=password)
        sv.start_server()

    elif mode == 'client':
        cl = client.Client(logger_client, redis_host=host, redis_port=port, redis_password=password)
        if cmd == 'deploy':
            model_onnx = Path(model_onnx) if model_onnx is not None else None
            custom_predict_py = Path(custom_predict_py) if custom_predict_py is not None else None
            if predict_type == 'Custom' and custom_predict_py is None:
                parser.print_help()
                exit(1)
            ret = cl.deploy(name, model_img_width, model_img_height, model_onnx, predict_type, custom_predict_py, timeout=timeout)
            common.print_format(ret, format, tm)

        elif cmd == 'deploy_list':
            ret = cl.deploy_list(timeout=timeout)
            common.print_format(ret, format, tm)

        elif cmd == 'undeploy':
            ret = cl.undeploy(name, timeout=timeout)
            common.print_format(ret, format, tm)

        elif cmd == 'start':
            ret = cl.start(name, model_provider=model_provider, timeout=timeout)
            common.print_format(ret, format, tm)

        elif cmd == 'stop':
            ret = cl.stop(name, timeout=timeout)
            common.print_format(ret, format, tm)

        elif cmd == 'predict':
            if image_file is not None:
                ret = cl.predict(name, image_file=Path(image_file), output_image_file=output_image_file, timeout=timeout)
                common.print_format(ret, format, tm)
            elif image_stdin:
                ret = cl.predict(name, image=sys.stdin.buffer.read(), output_image_file=output_image_file, timeout=timeout)
                common.print_format(ret, format, tm)
            else:
                common.print_format({"warn":f"Image file or stdin is empty."}, format, tm)

        elif cmd == 'predict_type_list':
            common.print_format([dict(predict_type=key,
                                      site=val['site'],
                                      image_width=val['image_width'],
                                      image_height=val['image_height']) for key,val in common.BASE_MODELS.items()], format, tm)
        else:
            common.print_format({"warn":f"Unkown command."}, format, tm)
            parser.print_help()

    else:
        parser.print_help()

