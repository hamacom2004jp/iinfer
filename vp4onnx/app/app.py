from vp4onnx.app import common
from vp4onnx.app import redis_client
from vp4onnx.app import redis_server
from pathlib import Path
import sys


def main(data_dir:Path,  boot_mode:str, redis_host:str, redis_port:int, cmd_type:str = None, cmd_name:str = None, cmd_timeout:int = 60,
         cmd_deploy_img_width:int = None, cmd_deploy_img_height:int = None, cmd_deploy_model_onnx:Path = None, cmd_deploy_postprocess_py:Path = None,
         cmd_predict_image_file:Path = None):
      """
      Redisサーバーまたはクライアントを起動し、コマンドを実行する。

      Args:
          data_dir (Path): データディレクトリのパス
          boot_mode (str): 起動モード。'server'または'client'のいずれか。
          redis_host (str): Redisサーバーのホスト名
          redis_port (int): Redisサーバーのポート番号
          cmd_type (str, optional): コマンドの種類。'deploy', 'undeploy', 'start', 'stop', 'predict'のいずれか。デフォルトはNone。
          cmd_name (str, optional): コマンドの名前。デフォルトはNone。
          cmd_timeout (int, optional): コマンドのタイムアウト時間（秒）。デフォルトは60。
          cmd_deploy_img_width (int, optional): デプロイする画像の幅。デフォルトはNone。
          cmd_deploy_img_height (int, optional): デプロイする画像の高さ。デフォルトはNone。
          cmd_deploy_model_onnx (Path, optional): デプロイするモデルのONNXファイルのパス。デフォルトはNone。
          cmd_deploy_postprocess_py (Path, optional): デプロイするモデルの後処理スクリプトのパス。デフォルトはNone。
          cmd_predict_image_file (Path, optional): 予測に使用する画像ファイルのパス。デフォルトはNone。

      Returns:
          str: コマンドの実行結果を表す文字列。
      """
      logger_client, logger_server, config = common.load_config()

      if boot_mode == 'server':
            logger_server.info(f"Starting server.")
            server = redis_server.RedisServer(data_dir, logger_server, redis_host=redis_host, redis_port=redis_port)
            server.start_server()
      else:
            logger_client.info(f"Start client.")
            client = redis_client.RedisClient(logger_client, redis_host=redis_host, redis_port=redis_port)
            if cmd_type == 'deploy':
                  ret = client.deploy(cmd_name, cmd_deploy_img_width, cmd_deploy_img_height, cmd_deploy_model_onnx, cmd_deploy_postprocess_py, timeout=cmd_timeout)
                  return ret
            elif cmd_type == 'undeploy':
                  ret = client.undeploy(cmd_name, timeout=cmd_timeout)
                  return ret
            elif cmd_type == 'start':
                  ret = client.start(cmd_name, timeout=cmd_timeout)
                  return ret
            elif cmd_type == 'stop':
                  ret = client.start(cmd_name, timeout=cmd_timeout)
                  return ret
            elif cmd_type == 'predict':
                  if cmd_predict_image_file is not None:
                        ret = client.predict(cmd_name, image_file=cmd_predict_image_file, timeout=cmd_timeout)
                        return ret
                  cmd_predict_image = sys.stdin.buffer.read()
                  ret = client.predict(cmd_name, image=cmd_predict_image, timeout=cmd_timeout)
                  return ret
