from pathlib import Path
from typing import Dict, Any, Union
import logging


class Train(object):
    def __init__(self, logger:logging.Logger) -> None:
        """
        このクラスのインスタンスを初期化します。
        継承時は、このコンストラクタを呼び出すようにしてください。
            super().__init__(logger)
        Args:
            logger (logging.Logger): ロガー
        """
        self.logger = logger

    def is_gpu_available(self, gpu_id:int=None) -> bool:
        """
        GPUが利用可能かどうかを返す関数です。
        戻り値がTrueの場合、GPUが利用可能です。
        戻り値がFalseの場合、GPUが利用不可です。

        Args:
            gpu_id (int, optional): GPU ID. Defaults to None.
        Returns:
            bool: GPUが利用可能かどうか
        """
        raise NotImplementedError()

    def train(self, deploy_dir:Path, model_conf_path:Path, train_cfg_options:Dict[str, Any]=None) -> None:
        """
        学習を実行する関数です。
        trainコマンド実行時に呼び出されます。
        この関数内でAIモデルの学習を行い完了するようにしてください。

        Args:
            deploy_dir (Path): デプロイディレクトリのパス
            model_conf_path (Path): モデル設定ファイルのパス
            train_cfg_options (Dict[str, Any]): 学習設定オプションのリスト
        """
        raise NotImplementedError()

    def post_train(self, deploy_dir:Path, conf:dict) -> None:
        """
        学習後の処理を行う関数です。
        trainコマンド実行時に呼び出されます。
        この関数内で学習後の処理を実装してください。
        
        Args:
            deploy_dir (Path): 学習ディレクトリのパス
            conf (dict): 学習設定
        """
        pass

class OnnxTrain(Train):
    def __init__(self, logger:logging.Logger) -> None:
        """
        このクラスのインスタンスを初期化します。
        継承時は、このコンストラクタを呼び出すようにしてください。
            super().__init__(logger)
        Args:
            logger (logging.Logger): ロガー
        """
        super().__init__(logger)

    def is_gpu_available(self, model_path:Union[Path,Any], model_conf_path:Path, gpu_id:int=None) -> bool:
        """
        GPUが利用可能かどうかを返す関数です。
        戻り値がTrueの場合、GPUが利用可能です。
        戻り値がFalseの場合、GPUが利用不可です。

        Args:
            model_path (Path|Any): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.
        Returns:
            bool: GPUが利用可能かどうか
        """
        try:
            import onnxruntime as rt
            rt.InferenceSession(model_path, providers=["CUDAExecutionProvider"], providers_options=[{'device_id': str(gpu_id)}])
            self.logger.info(f'GPU is available: True')
            return True
        except:
            self.logger.info(f'GPU is available: False')
            return False

class TorchTrain(Train):
    def __init__(self, logger:logging.Logger) -> None:
        """
        このクラスのインスタンスを初期化します。
        継承時は、このコンストラクタを呼び出すようにしてください。
            super().__init__(logger)
        Args:
            logger (logging.Logger): ロガー
        """
        super().__init__(logger)

    def is_gpu_available(self, model_path:Union[Path,Any], model_conf_path:Path, gpu_id:int=None) -> bool:
        """
        GPUが利用可能かどうかを返す関数です。
        戻り値がTrueの場合、GPUが利用可能です。
        戻り値がFalseの場合、GPUが利用不可です。

        Args:
            model_path (Path|Any): モデルファイルのパス
            model_conf_path (Path): モデル設定ファイルのパス
            gpu_id (int, optional): GPU ID. Defaults to None.
        Returns:
            bool: GPUが利用可能かどうか
        """
        try:
            import torch
            ret = torch.cuda.is_available()
            self.logger.info(f'GPU is available: {ret}')
            return ret
        except:
            self.logger.info(f'GPU is available: False')
            return False

