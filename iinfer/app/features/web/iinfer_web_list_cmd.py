from iinfer.app import common, web, feature
from typing import List, Dict, Any
import bottle
import glob
import json
import logging


class ListCmd(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/list_cmd', method='POST')
        def list_cmd():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            kwd = bottle.request.forms.get('kwd')
            ret = self.list_cmd(web, kwd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)


    def list_cmd(self, web:web.Web, kwd:str) -> List[Dict[str, Any]]:
        """
        コマンドファイルのタイトル一覧を取得する

        Args:
            web (web.Web): Webオブジェクト
            kwd (str): キーワード

        Returns:
            list: コマンドファイルのタイトル一覧
        """
        if kwd is None or kwd == '':
            kwd = '*'
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.list_cmd: kwd={kwd}")
        paths = glob.glob(str(web.cmds_path / f"cmd-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        ret = sorted(ret, key=lambda cmd: cmd["title"])
        return ret
