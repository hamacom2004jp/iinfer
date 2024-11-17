from iinfer.app import common, web, feature
import bottle
import json


class GetCmds(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/get_cmds', method='POST')
        def get_cmds():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            mode = bottle.request.forms.get('mode')
            ret = web.options.get_cmds(mode)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)
