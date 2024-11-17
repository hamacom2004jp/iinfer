from iinfer.app import common, web, feature
from typing import Dict, Any
import bottle
import json


class SaveCmd(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/save_cmd', method='POST')
        def save_cmd():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            title = bottle.request.forms.get('title')
            opt = bottle.request.forms.get('opt')
            ret = self.save_cmd(web, title, json.loads(opt))
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

    def save_cmd(self, web:web.Web, title:str, opt:Dict[str, Any]) -> Dict[str, str]:
        """
        コマンドファイルを保存する

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            dict: 結果
        """
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = web.cmds_path / f"cmd-{title}.json"
        web.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)
        return dict(success=f'Command "{title}" saved in "{opt_path}".')
