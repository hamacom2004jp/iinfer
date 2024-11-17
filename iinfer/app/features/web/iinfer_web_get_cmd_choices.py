from iinfer.app import common, web, feature
import bottle
import json


class GetCmdChoices(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/get_cmd_choices', method='POST')
        def get_cmd_choices():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            mode = bottle.request.forms.get('mode')
            cmd = bottle.request.forms.get('cmd')
            ret = web.options.get_cmd_choices(mode, cmd)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)
