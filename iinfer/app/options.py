from typing import List, Dict, Any 
from iinfer.app import feature
from iinfer.app.commons import module
import locale
import os

class Options:
    USE_REDIS_FALSE = -1
    USE_REDIS_MEIGHT = 0
    USE_REDIS_TRUE = 1
    DEFAULT_CAPTURE_MAXSIZE = 1024 * 1024 * 10
    def __init__(self):
        self._options = dict()
        self.init_options()

    def get_mode_keys(self) -> List[str]:
        return [key for key,val in self._options["mode"].items() if type(val) == dict]

    def get_modes(self) -> List[Dict[str, str]]:
        """
        起動モードの選択肢を取得します。
        Returns:
            List[Dict[str, str]]: 起動モードの選択肢
        """
        return [''] + [{key:val} for key,val in self._options["mode"].items() if type(val) == dict]

    def get_cmd_keys(self, mode:str) -> List[str]:
        if mode not in self._options["cmd"]:
            return []
        return [key for key,val in self._options["cmd"][mode].items() if type(val) == dict]

    def get_cmds(self, mode:str) -> List[Dict[str, str]]:
        """
        コマンドの選択肢を取得します。
        Args:
            mode: 起動モード
        Returns:
            List[Dict[str, str]]: コマンドの選択肢
        """
        if mode not in self._options["cmd"]:
            return ['Please select mode.']
        ret = [{key:val} for key,val in self._options["cmd"][mode].items() if type(val) == dict]
        if len(ret) > 0:
            return [''] + ret
        return ['Please select mode.']

    def get_cmd_attr(self, mode:str, cmd:str, attr:str) -> Any:
        """
        コマンドの属性を取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
            attr: 属性
        Returns:
            Any: 属性の値
        """
        if mode not in self._options["cmd"]:
            return [f'Unknown mode. ({mode})']
        if cmd is None or cmd == "" or cmd not in self._options["cmd"][mode]:
            return []
        if attr not in self._options["cmd"][mode][cmd]:
            return None
        return self._options["cmd"][mode][cmd][attr]
    
    def get_svcmd_feature(self, svcmd:str) -> feature.Feature:
        """
        サーバー側のコマンドのフューチャーを取得します。

        Args:
            svcmd: サーバー側のコマンド
        Returns:
            feature.Feature: フューチャー
        """
        if svcmd is None or svcmd == "":
            return None
        if svcmd not in self._options["svcmd"]:
            return None
        return self._options["svcmd"][svcmd]

    def get_cmd_choices(self, mode:str, cmd:str) -> List[Dict[str, Any]]:
        """
        コマンドのオプション一覧を取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
        Returns:
            List[Dict[str, Any]]: オプションの選択肢
        """
        return self.get_cmd_attr(mode, cmd, "choise")

    def get_cmd_opt(self, mode:str, cmd:str, opt:str) -> Dict[str, Any]:
        """
        コマンドのオプションを取得します。
        Args:
            mode: 起動モード
            cmd: コマンド
            opt: オプション
        Returns:
            Dict[str, Any]: オプションの値
        """
        opts = self.get_cmd_choices(mode, cmd)
        for o in opts:
            if 'opt' in o and o['opt'] == opt:
                return o
        return None

    def list_options(self):
        def _list(ret, key, val):
            if type(val) == dict and 'type' in val:
                opt = dict()
                if val['type'] == 'int':
                    opt['type'] = int
                    opt['action'] = 'append' if val['multi'] else None
                elif val['type'] == 'float':
                    opt['type'] = float
                    opt['action'] = 'append' if val['multi'] else None
                elif val['type'] == 'bool':
                    opt['type'] = None
                    opt['action'] = 'store_true'
                else:
                    opt['type'] = str
                    opt['action'] = 'append' if val['multi'] else None
                o = [f'-{val["short"]}'] if "short" in val else []
                o += [f'--{key}']
                language, _ = locale.getlocale()
                opt['help'] = val['discription_en'] if language.find('Japan') < 0 and language.find('ja_JP') < 0 else val['discription_ja']
                opt['default'] = val['default']
                opt['opts'] = o
                if val['choise'] is not None:
                    opt['choices'] = []
                    for c in val['choise']:
                        if type(c) == dict:
                            opt['choices'] += [c['opt']]
                        elif c is not None and c != "":
                            opt['choices'] += [c]
                else:
                    opt['choices'] = None
                ret[key] = opt
        ret = dict()
        for k, v in self._options.items():
            _list(ret, k, v)
        for mode in self._options["mode"]['choise']:
            for c, cmd in mode.items():
                if type(cmd) is not dict:
                    continue
                for opt in cmd["choise"]:
                    if type(opt) is not dict:
                        continue
                    _list(ret, opt['opt'], opt)
        return ret

    def mk_opt_list(self, opt:dict):
        opt_schema = self.get_cmd_choices(opt['mode'], opt['cmd'])
        opt_list = ['-m', opt['mode'], '-c', opt['cmd']]
        file_dict = dict()
        for key, val in opt.items():
            if key in ['stdout_log', 'capture_stdout']:
                continue
            schema = [schema for schema in opt_schema if schema['opt'] == key]
            if len(schema) == 0 or val == '':
                continue
            if schema[0]['type'] == 'bool':
                if val:
                    opt_list.append(f"--{key}")
                continue
            if type(val) == list:
                for v in val:
                    if v is None or v == '':
                        continue
                    opt_list.append(f"--{key}")
                    if str(v).find(' ') >= 0:
                        opt_list.append(f'"{v}"')
                    else:
                        opt_list.append(str(v))
            elif val is not None and val != '':
                opt_list.append(f"--{key}")
                if str(val).find(' ') >= 0:
                    opt_list.append(f'"{val}"')
                else:
                    opt_list.append(str(val))
            if 'fileio' in schema[0] and schema[0]['fileio'] == 'in' and type(val) != str:
                file_dict[key] = val
        return opt_list, file_dict

    def init_options(self):
        self._options = dict()
        self._options["version"] = dict(
            short="v", type="bool", default=None, required=False, multi=False, hide=True,
            discription_ja="バージョン表示",
            discription_en="Display version",
            choise=None)
        self._options["useopt"] = dict(
            short="u", type="str", default=None, required=False, multi=False, hide=True,
            discription_ja="オプションを保存しているファイルを使用します。",
            discription_en="Use the file that saves the options.",
            choise=None)
        self._options["saveopt"] = dict(
            short="s", type="bool", default=None, required=False, multi=False, hide=True,
            discription_ja="指定しているオプションを `-u` で指定したファイルに保存します。",
            discription_en="Save the specified options to the file specified by `-u`.",
            choise=[True, False])
        self._options["debug"] = dict(
            short="d", type="bool", default=False, required=False, multi=False, hide=True,
            discription_ja="デバックモードで起動します。",
            discription_en="Starts in debug mode.",
            choise=[True, False])
        self._options["format"] = dict(
            short="f", type="bool", default=None, required=False, multi=False, hide=True,
            discription_ja="処理結果を見やすい形式で出力します。指定しない場合json形式で出力します。",
            discription_en="Output the processing result in an easy-to-read format. If not specified, output in json format.",
            choise=None)
        self._options["mode"] = dict(
            short="m", type="str", default=None, required=True, multi=False, hide=True,
            discription_ja="起動モードを指定します。",
            discription_en="Specify the startup mode.",
            choise=[])
        self._options["cmd"] = dict(
            short="c", type="str", default=None, required=True, multi=False, hide=True,
            discription_ja="コマンドを指定します。",
            discription_en="Specify the command.",
            choise=[])
        # プラグイン読込み
        self._options["svcmd"] = dict()
        for mode, f in module.load_features('iinfer.app.features.cli').items():
            if mode not in self._options["cmd"]:
                self._options["cmd"][mode] = dict()
            for cmd, opt in f.items():
                 self._options["cmd"][mode][cmd] = opt
                 fobj:feature.Feature = opt['feature']
                 svcmd = fobj.get_svcmd()
                 if svcmd is not None:
                      self._options["svcmd"][svcmd] = fobj

        # デバックオプションを追加
        self._options["debug"]["opt"] = "debug"
        for key, mode in self._options["cmd"].items():
            if type(mode) is not dict:
                continue
            mode['opt'] = key
            for k, c in mode.items():
                if type(c) is not dict:
                    continue
                c["opt"] = k
                c["choise"].append(self._options["debug"])
                self._options["cmd"]["choise"] += [c]
            self._options["mode"][key] = mode
            self._options["mode"]["choise"] += [mode]

