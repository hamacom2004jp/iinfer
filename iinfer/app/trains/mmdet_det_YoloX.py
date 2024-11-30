from pathlib import Path
from iinfer.app import train
from typing import Dict, Any
import logging


SITE = 'https://github.com/open-mmlab/mmdetection/tree/main/configs/yolox'

class MMDetYoloX(train.TorchTrain):
    def __init__(self, logger:logging.Logger) -> None:
        super().__init__(logger)

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
        from mmengine.config import Config
        from mmengine.runner import Runner
        cfg = Config.fromfile(str(model_conf_path))
        cfg.work_dir = str(deploy_dir / "work_dirs")
        if train_cfg_options is not None:
            cfg.merge_from_dict(train_cfg_options)

        runner = Runner.from_cfg(cfg)
        runner.train()
