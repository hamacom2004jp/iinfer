from iinfer.app import web, feature
import bottle


class Showimg(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/showimg')
        def showimg():
            if not web.check_signin():
                return bottle.redirect('/signin/showimg')
            if web.showimg_html_data is not None:
                return web.showimg_html_data
            res:bottle.HTTPResponse = bottle.static_file('showimg.html', root=web.static_root)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return res
