from iinfer.app import common, web, feature
from typing import List, Dict, Any
import bottle
import glob
import json
import logging


class ListPipe(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/list_pipe', method='POST')
        def list_pipe():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            kwd = bottle.request.forms.get('kwd')
            ret = self.list_pipe(web, kwd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)


    def list_pipe(self, web:web.Web, kwd:str) -> List[Dict[str, Any]]:
        """
        パイプラインファイルのリストを取得する

        Args:
            web (web.Web): Webオブジェクト
            kwd (str): キーワード
        
        Returns:
            list: パイプラインファイルのリスト
        """
        if kwd is None or kwd == '':
            kwd = '*'
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.list_pipe: kwd={kwd}")
        paths = glob.glob(str(web.pipes_path / f"pipe-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        ret = sorted(ret, key=lambda cmd: cmd["title"])
        return ret
    