from iinfer.app import common, web, feature
from typing import Dict, Any
import bottle
import json
import logging


class LoadPipe(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/load_pipe', method='POST')
        def load_pipe():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            title = bottle.request.forms.get('title')
            ret = self.load_pipe(web, title)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

    def load_pipe(self, web:web.Web, title:str) -> Dict[str, Any]:
        """
        パイプラインを読み込む

        Args:
            web (web.Web): Webオブジェク
            title (str): タイトル

        Returns:
            dict: パイプラインの内容
        """
        opt_path = web.pipes_path / f"pipe-{title}.json"
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_pipe: title={title}")
        return common.loadopt(opt_path)
