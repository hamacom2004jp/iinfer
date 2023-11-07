from vp4onnx.app import common
from vp4onnx.app import redis_client
from vp4onnx.app import redis_server
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
    parser.add_argument('-p', '--password', help='Setting the redis server password.', required=True)
    subparsers = parser.add_subparsers(dest='boot_mode')
    server_parser = subparsers.add_parser('server', help='Start the server.')
    server_parser.add_argument('-d', '--data', help='Setting the data directory.', default=Path(HOME_DIR) / ".vp4onnx")

    client_parser = subparsers.add_parser('client', help='Start the client.')
    client_parser.add_argument('-n', '--name', help='Setting the cmd name.', default=None)
    client_parser.add_argument('-t', '--timeout', help='Setting the cmd timeout.', type=int, default=60)
    client_parser.add_argument('-f', '--format', help='Setting the cmd format.', action='store_true')

    client_subparsers = client_parser.add_subparsers(dest='cmd_type')
    predict_type_list_parser = client_subparsers.add_parser('predict_type_list', help='predict_type_list command.')
    deploy_parser = client_subparsers.add_parser('deploy', help='deploy command.')
    deploy_parser.add_argument('--model_img_width', help='Setting the cmd deploy model_img_width.', type=int, required=True)
    deploy_parser.add_argument('--model_img_height', help='Setting the cmd deploy model_img_height.', type=int, required=True)
    deploy_parser.add_argument('--model_onnx', help='Setting the cmd deploy model_onnx file.', required=True)
    deploy_parser.add_argument('--predict_type', help='Setting the cmd deploy predict_type. If Custom, custom_predict_py must be specified.', type=str,
                              choices=['Custom'] + list(common.BASE_MODELS.keys()), required=True)
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
            res = run(None, args.boot_mode, args.host, args.port, args.password,
                cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout,
                model_img_width=args.model_img_width, model_img_height=args.model_img_height,
                model_onnx=model_onnx, predict_type=args.predict_type, custom_predict_py=custom_predict_py)
            common.print_format(res, args.format, tm)
        elif args.cmd_type == 'start':
            res = run(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout, model_provider=args.model_provider)
            common.print_format(res, args.format, tm)
        elif args.cmd_type == 'predict':
            image_file = Path(args.image_file) if args.image_file is not None else None
            res = run(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout,
                     image_file=image_file, image_stdin=args.image_stdin, output_image_file=args.output_image_file)
            common.print_format(res, args.format, tm)
        elif args.cmd_type == 'predict_type_list':
            common.print_format([dict(predict_type=key,
                                      site=val['site'],
                                      image_width=val['image_width'],
                                      image_height=val['image_height']) for key,val in common.BASE_MODELS.items()], args.format, tm)
        elif args.cmd_type == 'deploy_list':
            res = run(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, timeout=args.timeout)
            common.print_format(res, args.format, tm)
        else:
            res = run(None, args.boot_mode, args.host, args.port, args.password, cmd_type=args.cmd_type, cmd_name=args.name, timeout=args.timeout)
            common.print_format(res, args.format, tm)
    elif args.boot_mode == 'server':
        if args.data is None:
            server_parser.print_help()
            exit(1)
        res = run(Path(args.data), args.boot_mode, args.host, args.port, args.password)
        common.print_format(res, args.format, tm)
    else:
        parser.print_help()


def run(data_dir:Path,  boot_mode:str, redis_host:str, redis_port:int, redis_password:str, cmd_type:str = None, cmd_name:str = None, timeout:int = 60,
         model_img_width:int = None, model_img_height:int = None, model_onnx:Path = None, predict_type:str = 'None', custom_predict_py:Path = None,
         model_provider:str = 'CPUExecutionProvider', image_file:Path = None, image_stdin:bool = False, output_image_file:Path = None):
      """
      サーバーまたはクライアントを起動し、コマンドを実行する。

      Args:
          data_dir (Path): データディレクトリのパス
          boot_mode (str): 起動モード。'server'または'client'のいずれか。
          redis_host (str): Redisサーバーのホスト名
          redis_port (int): Redisサーバーのポート番号
          redis_password (str): Redisサーバーのパスワード
          cmd_type (str, optional): コマンドの種類。'deploy', 'deploy_list', 'undeploy', 'start', 'stop', 'predict'のいずれか。デフォルトはNone。
          cmd_name (str, optional): コマンドの名前。デフォルトはNone。
          timeout (int, optional): コマンドのタイムアウト時間（秒）。デフォルトは60。
          model_img_width (int, optional): デプロイする画像の幅。デフォルトはNone。
          model_img_height (int, optional): デプロイする画像の高さ。デフォルトはNone。
          model_onnx (Path, optional): デプロイするモデルのONNXファイルのパス。デフォルトはNone。
          predict_type (str, optional): デプロイするモデルの推論方法のタイプ。デフォルトは'None'。
          custom_predict_py (Path, optional): デプロイするモデルの推論スクリプトのパス。デフォルトはNone。
          model_provider (str, optional): 推論実行時のモデルプロバイダー。
                                          'CPUExecutionProvider','CUDAExecutionProvider','TensorrtExecutionProvider'のいずれか。
                                          デフォルトは'CPUExecutionProvider'。
          image_file (Path, optional): 予測に使用する画像ファイルのパス。デフォルトはNone。
          image_stdin (bool, optional): 予測に使用する画像を標準入力から読み込むかどうか。デフォルトはFalse。
          output_image_file (Path, optional): 予測結果の画像ファイルのパス。デフォルトはNone。

      Returns:
          dict: コマンドの実行結果。
      """
      logger_client, logger_server, config = common.load_config()

      if boot_mode == 'server':
            logger_server.info(f"Starting server.")
            server = redis_server.RedisServer(data_dir, logger_server, redis_host=redis_host, redis_port=redis_port, redis_password=redis_password)
            server.start_server()
      else:
            logger_client.info(f"Start client.")
            client = redis_client.RedisClient(logger_client, redis_host=redis_host, redis_port=redis_port, redis_password=redis_password)
            if cmd_type == 'deploy':
                  ret = client.deploy(cmd_name, model_img_width, model_img_height, model_onnx, predict_type, custom_predict_py, timeout=timeout)
                  return ret
            elif cmd_type == 'deploy_list':
                  ret = client.deploy_list(timeout=timeout)
                  return ret
            elif cmd_type == 'undeploy':
                  ret = client.undeploy(cmd_name, timeout=timeout)
                  return ret
            elif cmd_type == 'start':
                  ret = client.start(cmd_name, model_provider=model_provider, timeout=timeout)
                  return ret
            elif cmd_type == 'stop':
                  ret = client.stop(cmd_name, timeout=timeout)
                  return ret
            elif cmd_type == 'predict':
                  if image_file is not None:
                        ret = client.predict(cmd_name, image_file=image_file, output_image_file=output_image_file, timeout=timeout)
                        return ret
                  if image_stdin:
                        ret = client.predict(cmd_name, image=sys.stdin.buffer.read(), output_image_file=output_image_file, timeout=timeout)
                        return ret
                  logger_client.warn(str({"warn":f"Image file or stdin is empty."}))
                  return {"warn":f"Image file or stdin is empty."}
      return {"warn":f"Unkown command."}
