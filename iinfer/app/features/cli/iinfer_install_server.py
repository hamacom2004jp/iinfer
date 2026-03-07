from cmdbox.app import common
from cmdbox.app.features.cli import cmdbox_cmdbox_server_install
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class InstallServer(cmdbox_cmdbox_server_install.CmdboxServerInstall):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'install'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'server'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "`推論サーバー` のdockerイメージを `build` します。`build` が成功すると、実行時ディレクトリに `docker-compose.yml` ファイルが生成されます。"
        opt['description_en'] = "`Build` the docker image of the `inference server`. If the `build` is successful, a `docker-compose.yml` file is generated in the execution directory."
        opt['choice'] += [
            dict(opt="install_iinfer", type=Options.T_STR, default='iinfer', required=False, multi=False, hide=True, choice=None,
                 description_ja=f"省略した時は `iinfer` を使用します。 `iinfer=={self.ver.__version__}` といった指定も可能です。",
                 description_en=f"When omitted, `iinfer` is used. You can also specify `iinfer=={self.ver.__version__}`.",
                 test_false={"win":"iinfer"}),
            dict(opt="install_onnx", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                 description_ja="dockerイメージ内に `onnxruntime` をインストールします。",
                 description_en="Install `onnxruntime` in the docker image."),
            dict(opt="install_mmdet", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                 description_ja="dockerイメージ内に `mmdetection` をインストールします。",
                 description_en="Install `mmdetection` in the docker image."),
            dict(opt="install_mmseg", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                 description_ja="dockerイメージ内に `mmsegmentation` をインストールします。",
                 description_en="Install `mmsegmentation` in the docker image."),
            dict(opt="install_mmpretrain", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                 description_ja="dockerイメージ内に `mmpretrain` をインストールします。",
                 description_en="Install `mmpretrain` in the docker image."),
            dict(opt="install_insightface", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                 description_ja="dockerイメージ内に `insightface` をインストールします。",
                 description_en="Install `insightface` in the docker image."),
        ]
        return opt

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.data is None:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        install_use_gpu_opt = '--install_use_gpu' if args.install_use_gpu else ''
        run_extra_post = args.run_extra_post if args.run_extra_post is not None and isinstance(args.run_extra_post, list) else []
        if args.install_onnx:
            run_extra_post.append(f'{self.ver.__appid__} -m install -c onnx {install_use_gpu_opt} --debug')
        if args.install_mmdet:
            run_extra_post.append(f'{self.ver.__appid__} -m install -c mmdet --data {args.data} {install_use_gpu_opt} --debug')
        if args.install_mmseg:
            run_extra_post.append(f'{self.ver.__appid__} -m install -c mmseg --data {args.data} {install_use_gpu_opt} --debug')
        if args.install_mmpretrain:
            run_extra_post.append(f'{self.ver.__appid__} -m install -c mmpretrain --data {args.data} {install_use_gpu_opt} --debug')
        if args.install_insightface:
            run_extra_post.append(f'{self.ver.__appid__} -m install -c insightface --data {args.data} {install_use_gpu_opt} --debug')
        install_extra = args.install_extra if args.install_extra is not None and isinstance(args.install_extra, list) else []
        install_extra.append(args.install_iinfer)
        if args.install_from is None:
            if args.install_use_gpu:
                args.install_from = "pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime"
            else:
                args.install_from = "python:3.11.9-slim"

        ret = self.server_install(logger, Path(args.data),
                                  install_cmdbox_tgt=args.install_cmdbox,
                                  install_from=args.install_from,
                                  install_no_python=args.install_no_python,
                                  install_compile_python=args.install_compile_python,
                                  install_tag=args.install_tag,
                                  install_use_gpu=args.install_use_gpu,
                                  tts_engine=args.tts_engine,
                                  voicevox_ver=args.voicevox_ver,
                                  voicevox_whl=args.voicevox_whl,
                                  run_extra_pre=args.run_extra_pre,
                                  run_extra_post=run_extra_post,
                                  install_extra=install_extra,
                                  compose_path=args.compose_path,
                                  language=args.language)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None
