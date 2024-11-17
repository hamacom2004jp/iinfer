from iinfer.app import web, feature
import bottle


class Annotation(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/annotation')
        def annotation():
            if not web.check_signin():
                return bottle.redirect(f'/signin/annotation')
            if web.anno_html_data is not None:
                return web.anno_html_data
            res:bottle.HTTPResponse = bottle.static_file('annotation.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res
