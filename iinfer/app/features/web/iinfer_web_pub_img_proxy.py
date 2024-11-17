from iinfer.app import common, web, feature
import bottle
import logging
import time


class PubImgProxy(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/webcap/pub_img/<port:int>', method='POST')
        def pub_img_proxy(port:int):
            """
            webcap画面から送信されてくる画像を、webcapプロセスに送信(プロキシ)する
            """
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.pub_img_proxy: port=http://localhost:{port}/webcap/pub_img, headers={dict(bottle.request.headers)}")
            if not bottle.request.content_type.startswith('multipart/form-data'):
                bottle.abort(400, 'Expected multipart request.')
                return
            try:
                tm = time.perf_counter()
                files = [['files',(fn, bottle.request.files[fn].file.read(), bottle.request.files[fn].content_type)] for fn in bottle.request.files.keys()]
                responce = web.webcap_client.post(f'http://localhost:{port}/webcap/pub_img', files=files)
                for h in responce.headers:
                    bottle.response.headers[h] = responce.headers[h]
                content = responce.content
                if web.logger.level == logging.DEBUG:
                    output_str = common.to_str(content.decode("utf-8"), slise=100)
                    web.logger.debug(f"web.pub_img_proxy: res_status={responce.status_code}, res_headers={responce.headers}, res_content={output_str}")
                bottle.response.status = responce.status_code
                return responce.content
            except Exception as e:
                web.logger.warning(f'web.start.pub_img_proxy: pub_img_proxy closed. {e}')
                bottle.abort(502, 'Could not connect to webcap process.')
                return
