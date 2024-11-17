from iinfer.app import common, web
from iinfer.app.features.web import iinfer_web_gui
from typing import Dict, Any
import bottle
import json
import logging


class LoadCmd(iinfer_web_gui.Gui):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/load_cmd', method='POST')
        def load_cmd():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            title = bottle.request.forms.get('title')
            ret = self.load_cmd(web, title)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

    def load_cmd(self, web:web.Web, title:str) -> Dict[str, Any]:
        """
        コマンドファイルを読み込む
        
        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            
        Returns:
            dict: コマンドファイルの内容
        """
        opt_path = web.cmds_path / f"cmd-{title}.json"
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_cmd: title={title}, opt_path={opt_path}")
        return common.loadopt(opt_path)
