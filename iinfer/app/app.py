from iinfer import version
from iinfer.app import common, client, options, server, web
from pathlib import Path
import argparse
import argcomplete
import logging
import time


def main(args_list:list=None):
    app = IinferApp()
    return app.main(args_list)[0]

class IinferApp:
    def __init__(self):
        self.sv = None
        self.cl = None
        self.web = None
        self.options = options.Options()

    def main(self, args_list:list=None, file_dict:dict=dict(), webcall:bool=False):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        parser = argparse.ArgumentParser(prog='iinfer', description='This application generates modules to set up the application system.')
        opts = self.options.list_options()
        for opt in opts.values():
            default = opt["default"] if opt["default"] is not None and opt["default"] != "" else None
            if opt["action"] is None:
                parser.add_argument(*opt["opts"], help=opt["help"], type=opt["type"], default=default, choices=opt["choices"])
            else:
                parser.add_argument(*opt["opts"], help=opt["help"], default=default, action=opt["action"])

        argcomplete.autocomplete(parser)
        # mainメソッドの起動時引数がある場合は、その引数を解析する
        if args_list is not None:
            args = parser.parse_args(args=args_list)
        else:
            args = parser.parse_args()
        # 起動時引数で指定されたオプションをファイルから読み込んだオプションで上書きする
        args_dict = vars(args)
        for key, val in file_dict.items():
            args_dict[key] = val
        # useoptオプションで指定されたオプションファイルを読み込む
        opt = common.loadopt(args.useopt)
        # 最終的に使用するオプションにマージする
        for key, val in args_dict.items():
            args_dict[key] = common.getopt(opt, key, preval=args_dict, withset=True)
        args = argparse.Namespace(**args_dict)

        tm = time.perf_counter()
        ret = {"success":f"Start command. {args}"}

        if args.saveopt:
            if args.useopt is None:
                msg = {"warn":f"Please specify the --useopt option."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg
            common.saveopt(opt, args.useopt)
            ret = {"success":f"Save options file. {args.useopt}"}

        if args.version:
            v = version.__logo__ + '\n' + version.__description__
            common.print_format(v, False, tm, None, False)
            return 0, v

        if args.mode is None:
            msg = {"warn":f"mode is None. Please specify the --help option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg

        common.mklogdir(args.data)
        common.copy_sample(args.data)
        common.copy_sample(Path.cwd())

        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data, webcall=webcall if args.cmd != 'webcap' else True)
        if logger.level == logging.DEBUG:
            logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}")

        feature = self.options.get_cmd_attr(args.mode, args.cmd, 'feature')
        if feature is not None:
            status, ret, obj = feature.apprun(logger, args, tm)
            if isinstance(obj, server.Server):
                self.sv = obj
            elif isinstance(obj, client.Client):
                self.cl = obj
            elif isinstance(obj, web.Web):
                self.web = obj
            return status, ret
        else:
            msg = {"warn":f"Unkown mode or cmd. mode={args.mode}, cmd={args.cmd}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg
