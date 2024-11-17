from iinfer.app import common, web, feature
import bottle
import json
import logging


class GetServerOpt(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/get_server_opt')
        def get_server_opt():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            opt = dict(host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname,
                       data=str(web.data), client_only=web.client_only)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.get_server_opt: opt={opt}")
            bottle.response.content_type = 'application/json'
            return json.dumps(opt)
