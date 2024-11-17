from iinfer import version
from iinfer.app import common, web, feature
import bottle
import json


class VersionsIinfer(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/versions_iinfer')
        def versions_iinfer():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            bottle.response.content_type = 'application/json'
            logo = [version.__logo__]
            return json.dumps(logo + version.__description__.split('\n'))
