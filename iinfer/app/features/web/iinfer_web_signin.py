from iinfer.app import web, feature
import bottle


class Signin(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/signin/<next>')
        def signin(next):
            if web.signin_html_data is not None:
                return web.signin_html_data
            res:bottle.HTTPResponse = bottle.static_file('signin.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res
