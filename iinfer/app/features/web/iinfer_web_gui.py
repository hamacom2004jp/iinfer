from iinfer.app import common, web, feature
from typing import Dict, Any
import bottle
import logging


class Gui(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui')
        def gui():
            if not web.check_signin():
                return bottle.redirect('/signin/gui')
            if web.gui_html_data is not None:
                return web.gui_html_data
            res:bottle.HTTPResponse = bottle.static_file('gui.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res

    def callback_console_modal_log_func(self, web:web.Web, output:Dict[str, Any]):
        """
        コンソールモーダルにログを出力する

        Args:
            web (web.Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_console_modal_log_func: output={output_str}")
        web.cb_queue.put(('js_console_modal_log_func', None, output))

    def callback_return_cmd_exec_func(self, web:web.Web, title:str, output:Dict[str, Any]):
        """
        コマンド実行結果を返す

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_cmd_exec_func: output={output_str}")
        web.cb_queue.put(('js_return_cmd_exec_func', title, output))

    def callback_return_pipe_exec_func(self, web:web.Web, title:str, output:Dict[str, Any]):
        """
        パイプライン実行結果を返す

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_pipe_exec_func: title={title}, output={output_str}")
        web.cb_queue.put(('js_return_pipe_exec_func', title, output))

    def callback_return_stream_log_func(self, web:web.Web, output:Dict[str, Any]):
        """
        ストリームログを返す

        Args:
            web (web.Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_stream_log_func: output={output_str}")
        web.cb_queue.put(('js_return_stream_log_func', None, output))

    def mk_curl_fileup(self, web:web.Web, cmd_opt:Dict[str, Any]) -> str:
        """
        curlコマンド文字列を作成する

        Args:
            cmd_opt (dict): コマンドのオプション
        
        Returns:
            str: curlコマンド文字列
        """
        if 'mode' not in cmd_opt or 'cmd' not in cmd_opt:
            return ""
        curl_fileup = set()
        for ref in web.options.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd']):
            if 'fileio' not in ref or ref['fileio'] != 'in':
                continue
            if ref['opt'] in cmd_opt and cmd_opt[ref['opt']] != '':
                curl_fileup.add(f'-F "{ref["opt"]}=@&lt;{ref["opt"]}&gt;"')
        if 'stdin' in cmd_opt and cmd_opt['stdin']:
            curl_fileup.add(f'-F "input_file=@&lt;input_file&gt;"')
        return " ".join(curl_fileup)
