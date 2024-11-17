from iinfer.app import web, feature
import bottle


class Usesignout(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/usesignout')
        @app.route('/signin/usesignout')
        def usesignout():
            if web.signin_file is not None:
                return dict(success={'usesignout': True})
            return dict(success={'usesignout': False})
