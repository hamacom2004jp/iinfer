from pathlib import Path
import argparse
import os


HOME_DIR = os.path.expanduser("~")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='python -m vp4onnx',
        description='This application generates modules to set up the application system.')
    parser.add_argument('--host', help='Setting the redis server host.', default='localhost')
    parser.add_argument('--port', help='Setting the redis server port.', type=int, default=6379)
    subparsers = parser.add_subparsers(dest='boot_mode')
    server_parser = subparsers.add_parser('server', help='Start the server.')
    server_parser.add_argument('-d', '--data', help='Setting the data directory.', default=Path(HOME_DIR) / ".vp4onnx")

    client_parser = subparsers.add_parser('client', help='Start the client.')
    client_parser.add_argument('-n', '--name', help='Setting the cmd name.', required=True)
    client_parser.add_argument('-t', '--timeout', help='Setting the cmd timeout.', type=int, default=60)

    client_subparsers = client_parser.add_subparsers(dest='cmd_type')
    deploy_parser = client_subparsers.add_parser('deploy', help='deploy command.')
    deploy_parser.add_argument('--img_width', help='Setting the cmd deploy img_width.', type=int, required=True)
    deploy_parser.add_argument('--img_height', help='Setting the cmd deploy img_height.', type=int, required=True)
    deploy_parser.add_argument('--model_onnx', help='Setting the cmd deploy model_onnx file.', required=True)
    deploy_parser.add_argument('--postprocess_py', help='Setting the cmd deploy postprocess_py file.', required=True)
    undeploy_parser = client_subparsers.add_parser('undeploy', help='undeploy command.')
    start_parser = client_subparsers.add_parser('start', help='start command.')
    stop_parser = client_subparsers.add_parser('stop', help='stop command.')
    predict_parser = client_subparsers.add_parser('predict', help='predict command.')
    predict_parser.add_argument('--image_file', help='Setting the cmd predict image file. Can also be specified with stdin.', default=None)

    args = parser.parse_args()
    from vp4onnx.app import app
    if args.boot_mode == 'client':
        if args.name is None:
            client_parser.print_help()
            exit(1)
        if args.cmd_type is None:
            client_parser.print_help()
            exit(1)
        if args.cmd_type == 'deploy':
            model_onnx = Path(args.model_onnx) if args.model_onnx is not None else None
            postprocess_py = Path(args.postprocess_py) if args.postprocess_py is not None else None
            app.main(None, args.boot_mode, args.host, args.port,
                 cmd_type=args.cmd_type, cmd_name=args.name, cmd_timeout=args.timeout,
                cmd_deploy_img_width=args.img_width, cmd_deploy_img_height=args.img_height,
                cmd_deploy_model_onnx=model_onnx, cmd_deploy_postprocess_py=postprocess_py)
        elif args.cmd_type == 'predict':
            image_file = Path(args.image_file) if args.image_file is not None else None
            app.main(None, args.boot_mode, args.host, args.port, cmd_type=args.cmd_type, cmd_name=args.name, cmd_timeout=args.timeout, cmd_predict_image_file=image_file)
        else:
            app.main(None, args.boot_mode, args.host, args.port, cmd_type=args.cmd_type, cmd_name=args.name, cmd_timeout=args.timeout)
    elif args.boot_mode == 'server':
        if args.data is None:
            server_parser.print_help()
            exit(1)
        app.main(Path(args.data), args.boot_mode, args.host, args.port)
    else:
        parser.print_help()
