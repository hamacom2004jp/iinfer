from iinfer.app import web, feature
import bottle
import logging


class BbforceCmd(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/bbforce_cmd')
        def bbforce_cmd():
            if not web.check_signin():
                return bottle.redirect('/signin/bbforce_cmd')
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.bbforce_cmd")
            try:
                web.container['iinfer_app'].sv.is_running = False
            except Exception as e:
                pass
            try:
                web.container['iinfer_app'].cl.is_running = False
            except Exception as e:
                pass
            try:
                web.container['iinfer_app'].web.is_running = False
            except Exception as e:
                pass
            try:
            #    web.container['pipe_proc'].send_signal(signal.CTRL_C_EVENT)
                web.container['pipe_proc'].terminate()
            except Exception as e:
                pass
            return dict(success='bbforce_cmd')

