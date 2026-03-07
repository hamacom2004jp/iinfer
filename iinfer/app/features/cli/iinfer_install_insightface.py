from cmdbox.app import common
from iinfer.app.features.cli import iinfer_install_onnx
from typing import Dict, Any, Union, Tuple, List
import argparse
import logging


class InstallInsightface(iinfer_install_onnx.InstallOnnx):
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
        return 'insightface'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "`insightface` をインストールします。"
        opt['description_en'] = "Install `insightface`."
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
        ret = self.insightface(logger, install_use_gpu=args.install_use_gpu)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def insightface(self, logger:logging.Logger, install_use_gpu:bool=False):
        returncode, _, _cmd = common.cmd('pip install cython', logger=logger, slise=-1)
        if returncode != 0:
            logger.warning(f"Failed to install cython. cmd:{_cmd}")
            return {"error": f"Failed to install cython. cmd:{_cmd}"}
        ret = self.onnx(logger, install_use_gpu)
        if "error" in ret: return ret
        returncode, _, _cmd = common.cmd('python -m pip install --upgrade pip setuptools', logger=logger, slise=-1)
        if returncode != 0:
            logger.warning(f"Failed to install setuptools. cmd:{_cmd}")
            return {"error": f"Failed to install setuptools. cmd:{_cmd}"}
        returncode, _, _cmd = common.cmd('pip install insightface', logger=logger, slise=-1)
        if returncode != 0:
            logger.warning(f"Failed to install insightface. cmd:{_cmd}")
            return {"error": f"Failed to install insightface. cmd:{_cmd}"}
        return {"success": f"Success to install insightface."}
