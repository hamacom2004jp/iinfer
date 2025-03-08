from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.options import Options
from iinfer.app import install
from pathlib import Path
from typing import Dict, Any, Tuple, Union, List
import argparse
import logging


class InstallServer(feature.UnsupportEdgeFeature):
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
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            discription_ja="`推論サーバー` のdockerイメージを `build` します。`build` が成功すると、実行時ディレクトリに `docker-compose.yml` ファイルが生成されます。",
            discription_en="`Build` the docker image of the `inference server`. If the `build` is successful, a `docker-compose.yml` file is generated in the execution directory.",
            choice=[
                dict(opt="data", type=Options.T_FILE, default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は f`$HONE/.{version.__appid__}` を使用します。",
                     discription_en="When omitted, f`$HONE/.{version.__appid__}` is used."),
                dict(opt="install_cmdbox", type=Options.T_STR, default='cmdbox', required=False, multi=False, hide=True, choice=None,
                     discription_ja=f"省略した時は `cmdbox` を使用します。 `cmdbox=={version.__version__}` といった指定も可能です。",
                     discription_en=f"When omitted, `cmdbox` is used. You can also specify `cmdbox=={version.__version__}`.",
                     test_false={"win":"cmdbox"}),
                dict(opt="install_iinfer", type=Options.T_STR, default='iinfer', required=False, multi=False, hide=True, choice=None,
                     discription_ja=f"省略した時は `iinfer` を使用します。 `iinfer=={self.ver.__version__}` といった指定も可能です。",
                     discription_en=f"When omitted, `iinfer` is used. You can also specify `iinfer=={self.ver.__version__}`.",
                     test_false={"win":"iinfer"}),
                dict(opt="install_onnx", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `onnxruntime` をインストールします。",
                     discription_en="Install `onnxruntime` in the docker image."),
                dict(opt="install_mmdet", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `mmdetection` をインストールします。",
                     discription_en="Install `mmdetection` in the docker image."),
                dict(opt="install_mmseg", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `mmsegmentation` をインストールします。",
                     discription_en="Install `mmsegmentation` in the docker image."),
                dict(opt="install_mmcls", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `mmclassification` をインストールします。",
                     discription_en="Install `mmclassification` in the docker image."),
                dict(opt="install_mmpretrain", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `mmpretrain` をインストールします。",
                     discription_en="Install `mmpretrain` in the docker image."),
                dict(opt="install_insightface", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="dockerイメージ内に `insightface` をインストールします。",
                     discription_en="Install `insightface` in the docker image."),
                dict(opt="install_from", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="作成するdockerイメージの元となるFROMイメージを指定します。",
                     discription_en="Specify the FROM image that will be the source of the docker image to be created."),
                dict(opt="install_no_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="pythonのインストールを行わないようにします。",
                     discription_en="Do not install python."),
                dict(opt="install_compile_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="python3をコンパイルしてインストールします。install_no_pythonが指定されるとそちらを優先します。",
                     discription_en="Compile and install python3; if install_no_python is specified, it is preferred."),
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     discription_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="install_use_gpu", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     discription_ja="GPUを使用するモジュール構成でインストールします。",
                     discription_en="Install with a module configuration that uses the GPU."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="処理結果jsonの保存先ファイルを指定。",
                     discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="処理結果jsonファイルを追記保存します。",
                     discription_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

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
        inst = install.Install(logger=logger, wsl_name=args.wsl_name, wsl_user=args.wsl_user)

        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg
        ret = inst.server(Path(args.data),
                          install_cmdbox_tgt=args.install_cmdbox,
                          install_iinfer_tgt=args.install_iinfer,
                          install_onnx=args.install_onnx,
                          install_mmdet=args.install_mmdet,
                          install_mmseg=args.install_mmseg,
                          install_mmcls=args.install_mmcls,
                          install_mmpretrain=args.install_mmpretrain,
                          install_insightface=args.install_insightface,
                          install_from=args.install_from,
                          install_no_python=args.install_no_python,
                          install_compile_python=args.install_compile_python,
                          install_tag=args.install_tag, install_use_gpu=args.install_use_gpu)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return 1, ret, inst
        return 0, ret, inst
