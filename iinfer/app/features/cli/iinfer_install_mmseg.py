from cmdbox.app import common
from cmdbox.app.options import Options
from iinfer.app.features.cli import iinfer_install_mmcv
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging
import shutil


class InstallMmseg(iinfer_install_mmcv.InstallMmcv):
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
        return 'mmseg'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "`mmsegmentation` をインストールします。"
        opt['description_en'] = "Install `mmsegmentation`."
        opt['choice'] += [
            dict(opt="data", type=Options.T_DIR, default=self.default_data, required=True, multi=False, hide=False, choice=None, web="mask",
                 description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                 description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
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
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg
        ret = self.mmseg(logger, Path(args.data), install_use_gpu=args.install_use_gpu)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def mmseg(self, logger:logging.Logger, data_dir:Path, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd(f'git clone -b main https://github.com/open-mmlab/mmsegmentation.git', logger=logger, slise=-1)
        if returncode != 0:
            logger.warning(f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists. cmd:{_cmd}")
            return {"error": f"Failed to git clone mmsegmentation. Delete mmsegmentation as it probably already exists. cmd:{_cmd}"}
        srcdir = Path('.') / 'mmsegmentation'
        shutil.copytree(srcdir, data_dir / 'mmsegmentation', dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
        shutil.rmtree(srcdir, ignore_errors=True)

        ret = self._openmin(install_use_gpu)
        if "error" in ret: return ret
        ret = self._mmcv(install_use_gpu)
        if "error" in ret: return ret
        msg = self._numpy()
        if "success" not in msg: return msg

        ret, _, _cmd = common.cmd('mim install mmsegmentation', logger=logger, slise=-1)
        if ret != 0:
            logger.warning(f"Failed to install mmsegmentation. cmd:{_cmd}")
            return {"error": f"Failed to install mmsegmentation. cmd:{_cmd}"}

        ret, _, _cmd = common.cmd('pip install ftfy', logger=logger, slise=-1)
        if ret != 0:
            logger.warning(f"Failed to install ftfy. cmd:{_cmd}")
            return {"error": f"Failed to install ftfy. cmd:{_cmd}"}

        ret, _, _cmd = common.cmd('pip install regex', logger=logger, slise=-1)
        if ret != 0:
            logger.warning(f"Failed to install regex. cmd:{_cmd}")
            return {"error": f"Failed to install regex. cmd:{_cmd}"}

        if srcdir.exists():
            return {"success": f"Please remove '{srcdir / 'mmsegmentation'}' manually."}
        return {"success": f"Success to install mmsegmentation."}
