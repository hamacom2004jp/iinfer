from iinfer import version
from iinfer.app import common, web, feature
import bottle


class Copyright(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/copyright')
        def copyright():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            return version.__copyright__

