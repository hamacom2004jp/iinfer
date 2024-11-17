from iinfer.app import common, web, feature
import bottle
import json


class DelCmd(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/del_cmd', method='POST')
        def del_cmd():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            title = bottle.request.forms.get('title')
            web.del_cmd(title)
            bottle.response.content_type = 'application/json'
            return json.dumps({}, default=common.default_json_enc)

    def del_cmd(self, web:web.Web, title:str):
        """
        コマンドファイルを削除する

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
        """
        opt_path = web.cmds_path / f"cmd-{title}.json"
        web.logger.info(f"del_cmd: opt_path={opt_path}")
        opt_path.unlink()
