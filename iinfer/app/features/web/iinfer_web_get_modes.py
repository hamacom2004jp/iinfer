from iinfer.app import common, web, feature
import bottle
import json


class GetModes(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/get_modes')
        def get_modes():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            ret = web.options.get_modes()
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

