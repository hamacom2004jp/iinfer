from iinfer.app import web, feature
import bottle
import logging


class Assets(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/assets/<filename:path>')
        def assets(filename):
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.assets: filename={filename}")
            return bottle.static_file(filename, root=web.static_root / 'assets')
