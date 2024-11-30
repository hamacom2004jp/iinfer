from pathlib import Path
from iinfer.app import train
from typing import Dict, Any
import argparse
import copy
import logging
import os
import time
import warnings


SITE = 'https://github.com/open-mmlab/mmpretrain/tree/master/configs/swin_transformer'

class MMPretrainClsSwin(train.TorchTrain):
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
        from mmcv.runner import get_dist_info, init_dist
        from mmcv import Config
        from mmcls import __version__
        from mmcls.apis import init_random_seed, set_random_seed, train_model
        from mmcls.datasets import build_dataset
        from mmcls.models import build_classifier
        from mmcls.utils import (auto_select_device, collect_env, get_root_logger,
                                setup_multi_processes)
        import mmcv
        import torch

        args = argparse.Namespace(**train_cfg_options)

        cfg = Config.fromfile(str(model_conf_path))
        cfg.work_dir = str(deploy_dir / "work_dirs")
        if train_cfg_options is not None:
            cfg.merge_from_dict(train_cfg_options)

        # set multi-process settings
        setup_multi_processes(cfg)

        # set cudnn_benchmark
        if cfg.get('cudnn_benchmark', False):
            torch.backends.cudnn.benchmark = True

        # work_dir is determined in this priority: CLI > segment in file > filename
        if args.work_dir is not None:
            # update configs according to CLI args if args.work_dir is not None
            cfg.work_dir = args.work_dir
        elif cfg.get('work_dir', None) is None:
            # use config filename as default work_dir if cfg.work_dir is None
            cfg.work_dir = os.path.join('./work_dirs',
                                    os.path.splitext(os.path.basename(args.config))[0])
        if args.resume_from is not None:
            cfg.resume_from = args.resume_from
        if args.gpus is not None:
            cfg.gpu_ids = range(1)
            warnings.warn('`--gpus` is deprecated because we only support '
                        'single GPU mode in non-distributed training. '
                        'Use `gpus=1` now.')
        if args.gpu_ids is not None:
            cfg.gpu_ids = args.gpu_ids[0:1]
            warnings.warn('`--gpu-ids` is deprecated, please use `--gpu-id`. '
                        'Because we only support single GPU mode in '
                        'non-distributed training. Use the first GPU '
                        'in `gpu_ids` now.')
        if args.gpus is None and args.gpu_ids is None:
            cfg.gpu_ids = [args.gpu_id]

        if args.ipu_replicas is not None:
            cfg.ipu_replicas = args.ipu_replicas
            args.device = 'ipu'

        # init distributed env first, since logger depends on the dist info.
        if args.launcher == 'none':
            distributed = False
        else:
            distributed = True
            init_dist(args.launcher, **cfg.dist_params)
            _, world_size = get_dist_info()
            cfg.gpu_ids = range(world_size)

        # create work_dir
        mmcv.mkdir_or_exist(os.path.abspath(cfg.work_dir))
        # dump config
        cfg.dump(os.path.join(cfg.work_dir, os.path.basename(args.config)))
        # init the logger before other steps
        timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
        log_file = os.path.join(cfg.work_dir, f'{timestamp}.log')
        logger = get_root_logger(log_file=log_file, log_level=cfg.log_level)

        # init the meta dict to record some important information such as
        # environment info and seed, which will be logged
        meta = dict()
        # log env info
        env_info_dict = collect_env()
        env_info = '\n'.join([(f'{k}: {v}') for k, v in env_info_dict.items()])
        dash_line = '-' * 60 + '\n'
        logger.info('Environment info:\n' + dash_line + env_info + '\n' +
                    dash_line)
        meta['env_info'] = env_info

        # log some basic info
        logger.info(f'Distributed training: {distributed}')
        logger.info(f'Config:\n{cfg.pretty_text}')

        # set random seeds
        cfg.device = args.device or auto_select_device()
        seed = init_random_seed(args.seed, device=cfg.device)
        seed = seed + torch.distributed.get_rank() if args.diff_seed else seed
        logger.info(f'Set random seed to {seed}, '
                    f'deterministic: {args.deterministic}')
        set_random_seed(seed, deterministic=args.deterministic)
        cfg.seed = seed
        meta['seed'] = seed

        model = build_classifier(cfg.model)
        model.init_weights()

        datasets = [build_dataset(cfg.data.train)]
        if len(cfg.workflow) == 2:
            val_dataset = copy.deepcopy(cfg.data.val)
            val_dataset.pipeline = cfg.data.train.pipeline
            datasets.append(build_dataset(val_dataset))

        # save mmcls version, config file content and class names in
        # runner as meta data
        meta.update(
            dict(
                mmcls_version=__version__,
                config=cfg.pretty_text,
                CLASSES=datasets[0].CLASSES))

        # add an attribute for visualization convenience
        train_model(
            model,
            datasets,
            cfg,
            distributed=distributed,
            validate=(not args.no_validate),
            timestamp=timestamp,
            device=cfg.device,
            meta=meta)
