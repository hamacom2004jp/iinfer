from iinfer.app import web, feature
import bottle


class DoSignout(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/signout/<next>')
        def do_signout(next):
            session = bottle.request.environ.get('beaker.session')
            session.delete()
            bottle.redirect(f'/{next}')
