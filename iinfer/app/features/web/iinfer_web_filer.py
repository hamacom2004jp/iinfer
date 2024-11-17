from iinfer.app import web, feature
import bottle


class Filer(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/filer')
        def filer():
            if not web.check_signin():
                return bottle.redirect('/signin/filer')
            if web.filer_html_data is not None:
                return web.filer_html_data
            res:bottle.HTTPResponse = bottle.static_file('filer.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res
