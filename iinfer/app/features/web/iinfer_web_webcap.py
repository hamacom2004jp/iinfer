from iinfer.app import web, feature
import bottle


class Webcap(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/webcap')
        def webcap():
            if not web.check_signin():
                return bottle.redirect(f'/signin/webcap')
            if web.webcap_html_data is not None:
                return web.webcap_html_data
            res:bottle.HTTPResponse = bottle.static_file('webcap.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res
