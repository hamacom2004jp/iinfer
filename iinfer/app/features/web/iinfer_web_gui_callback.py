from iinfer.app import common, web, feature
import bottle
import gevent
import logging
import json
import queue


class GuiCallback(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/callback')
        def gui_callback():
            if not web.check_signin():
                bottle.abort(401, 'Please log in to retrieve session.')
                return
            return self.gui_callback(web)

    def gui_callback(self, web:web.Web):
        """
        コマンドの実行結果をキューから取り出してブラウザに送信する

        Args:
            web (web.Web): Webオブジェクト
        """
        wsock = bottle.request.environ.get('wsgi.websocket') # type: ignore
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.gui_callback: connected")
        if not wsock:
            bottle.abort(400, 'Expected WebSocket request.')
            return
        while True:
            outputs = None
            try:
                cmd, title, output = web.cb_queue.get(block=True, timeout=0.001)
                if web.logger.level == logging.DEBUG:
                    output_str = common.to_str(output, slise=100)
                    web.logger.debug(f"web.gui_callback: cmd={cmd}, title={title}, output={output_str}")
                outputs = dict(cmd=cmd, title=title, output=output)
                wsock.send(json.dumps(outputs, default=common.default_json_enc))
            except queue.Empty:
                gevent.sleep(0.001)
            except Exception as e:
                web.logger.warning(f'web.gui_callback: websocket error. {e}')
                bottle.abort(400, 'Expected WebSocket request.')
                return
