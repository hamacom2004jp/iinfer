from pathlib import Path
from tabulate import tabulate
import argparse
import os
import time


HOME_DIR = os.path.expanduser("~")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python -m vp4onnx',
        description='This application generates modules to set up the application system.')
    parser.add_argument('--host', help='Setting the redis server host.', default='localhost')
    parser.add_argument('--port', help='Setting the redis server port.', type=int, default=6379)
    parser.add_argument('-p', '--password', help='Setting the redis server password.', required=True)
    subparsers = parser.add_subparsers(dest='boot_mode')
    server_parser = subparsers.add_parser('server', help='Start the server.')
    server_parser.add_argument('-d', '--data', help='Setting the data directory.', default=Path(HOME_DIR) / ".vp4onnx")

    client_parser = subparsers.add_parser('client', help='Start the client.')
    client_parser.add_argument('-n', '--name', help='Setting the cmd name.', default=None)
    client_parser.add_argument('-t', '--timeout', help='Setting the cmd timeout.', type=int, default=60)
    client_parser.add_argument('-f', '--format', help='Setting the cmd format.', action='store_true')

    client_subparsers = client_parser.add_subparsers(dest='cmd_type')
    deploy_parser = client_subparsers.add_parser('deploy', help='deploy command.')
    deploy_parser.add_argument('--model_img_width', help='Setting the cmd deploy model_img_width.', type=int, required=True)
    deploy_parser.add_argument('--model_img_height', help='Setting the cmd deploy model_img_height.', type=int, required=True)
    deploy_parser.add_argument('--model_onnx', help='Setting the cmd deploy model_onnx file.', required=True)
    deploy_parser.add_argument('--predict_type', help='Setting the cmd deploy predict_type. If Custom, custom_predict_py must be specified.', type=str,
                              choices=['Custom', 'ObjectDetection_YoloV3'],
                              default='ObjectDetection_YoloV3')
    deploy_parser.add_argument('--custom_predict_py', help='Setting the cmd deploy custom_predict.py file.', default=None)
    deploy_list_parser = client_subparsers.add_parser('deploy_list', help='deploy_list command.')
    undeploy_parser = client_subparsers.add_parser('undeploy', help='undeploy command.')
    start_parser = client_subparsers.add_parser('start', help='start command.')
    start_parser.add_argument('--model_provider', help='Setting the cmd start model_provider.', type=str,
                              choices=['CPUExecutionProvider','CUDAExecutionProvider','TensorrtExecutionProvider'], default='CPUExecutionProvider')
    stop_parser = client_subparsers.add_parser('stop', help='stop command.')
    predict_parser = client_subparsers.add_parser('predict', help='predict command.')
    predict_parser.add_argument('-i', '--image_file', help='Setting the cmd predict image file.', default=None)
    predict_parser.add_argument('-o', '--output_image_file', help='Setting the cmd predict output image file.', default=None)
    predict_parser.add_argument('--image_stdin', help='Setting the cmd predict image for stdin.', action='store_true')

    args = parser.parse_args()
    tm = time.time()
    from vp4onnx.app import app
    def print_format(data:dict, format:bool, tm:float):
        if format:
            if 'success' in data and type(data['success']) == list:
                print(tabulate(data['success'], headers='keys'))
            elif 'success' in data:
                print(tabulate([data['success']], headers='keys'))
            else:
                print(tabulate([data], headers='keys'))
            print(f"{time.time() - tm:.03f} seconds.")
        else:
            print(data)
    if args.boot_mode == 'client':
        if args.cmd_type is None:
            client_parser.print_help()
            exit(1)
        if args.cmd_type == 'deploy':
            model_onnx = Path(args.model_onnx) if args.model_onnx is not None else None
            custom_predict_py = Path(args.custom_predict_py) if args.custom_predict_py is not None else None
            if args.predict_type == 'Custom' and args.custom_predict_py is None:
                deploy_parser.print_help()
                exit(1)
            res = app.main(None, args.boot_mode, args.host, args.port, args.password,
                cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout,
                model_img_width=args.model_img_width, model_img_height=args.model_img_height,
                model_onnx=model_onnx, predict_type=args.predict_type, custom_predict_py=custom_predict_py)
            print_format(res, args.format, tm)
        elif args.cmd_type == 'start':
            res = app.main(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout, model_provider=args.model_provider)
            print_format(res, args.format, tm)
        elif args.cmd_type == 'predict':
            image_file = Path(args.image_file) if args.image_file is not None else None
            res = app.main(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout,
                     image_file=image_file, image_stdin=args.image_stdin, output_image_file=args.output_image_file)
            print_format(res, args.format, tm)
        elif args.cmd_type == 'deploy_list':
            res = app.main(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, timeout=args.timeout)
            print_format(res, args.format, tm)
        else:
            res = app.main(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout)
            print_format(res, args.format, tm)
    elif args.boot_mode == 'server':
        if args.data is None:
            server_parser.print_help()
            exit(1)
        res = app.main(Path(args.data), args.boot_mode, args.host, args.port, args.password)
        print_format(res, args.format, tm)
    else:
        parser.print_help()
