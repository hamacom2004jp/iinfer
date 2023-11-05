from vp4onnx.app import common
from vp4onnx.app import redis_client
from vp4onnx.app import redis_server
from pathlib import Path
import sys


def main(data_dir:Path,  boot_mode:str, redis_host:str, redis_port:int, redis_password:str, cmd_type:str = None, cmd_name:str = None, timeout:int = 60,
         model_img_width:int = None, model_img_height:int = None, model_onnx:Path = None, predict_type:str = 'None', custom_predict_py:Path = None,
         model_provider:str = 'CPUExecutionProvider', image_file:Path = None, image_stdin:bool = False, output_image_file:Path = None):
      """
      Redisサーバーまたはクライアントを起動し、コマンドを実行する。

      Args:
          data_dir (Path): データディレクトリのパス
          boot_mode (str): 起動モード。'server'または'client'のいずれか。
          redis_host (str): Redisサーバーのホスト名
          redis_port (int): Redisサーバーのポート番号
          redis_password (str): Redisサーバーのパスワード
          cmd_type (str, optional): コマンドの種類。'deploy', 'undeploy', 'start', 'stop', 'predict'のいずれか。デフォルトはNone。
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
          str: コマンドの実行結果を表す文字列。
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
