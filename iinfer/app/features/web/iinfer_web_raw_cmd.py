from iinfer.app import common, web, feature
from iinfer.app.features.web import iinfer_web_gui
from typing import List, Dict, Any
import bottle
import json
import logging


class RawCmd(iinfer_web_gui.Gui):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/raw_cmd', method='POST')
        def raw_cmd():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.raw_cmd(web, title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

    def raw_cmd(self, web:web.Web, title:str, opt:dict) -> List[Dict[str, Any]]:
        """
        コマンドライン文字列、オプション文字列、curlコマンド文字列を作成する

        Args:
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            list[Dict[str, Any]]: コマンドライン文字列、オプション文字列、curlコマンド文字列
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.raw_cmd: title={title}, opt={opt}")
        opt_list, _ = web.options.mk_opt_list(opt)
        if 'stdout_log' in opt: del opt['stdout_log']
        if 'capture_stdout' in opt: del opt['capture_stdout']
        curl_cmd_file = self.mk_curl_fileup(web, opt)
        return [dict(type='cmdline',raw=' '.join(['python','-m','iinfer']+opt_list)),
                dict(type='optjson',raw=json.dumps(opt, default=common.default_json_enc)),
                dict(type='curlcmd',raw=f'curl {curl_cmd_file} http://localhost:8081/exec_cmd/{title}')]
