from iinfer.app import common, web, feature
import bottle
import logging
import time
import traceback


class PubImg(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/showimg/pub_img', method='POST')
        def pub_img():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            try:
                tm = time.time()
                if bottle.request.content_type.startswith('multipart/form-data'):
                    for fn in bottle.request.files.keys():
                        filename = bottle.request.files[fn].filename
                        web.img_queue.put((filename, bottle.request.files[fn].file.read()))
                        if web.logger.level == logging.DEBUG:
                            web.logger.debug(f"web.pub_img: filename={filename}")
                else:
                    raise ValueError('Expected multipart request.')
                ret = common.to_str(dict(success='Added to queue.'))
                return ret
            except:
                web.logger.warning('pub_img error', exc_info=True)
                return common.to_str(dict(warn=f'pub_img error. {traceback.format_exc()}'))
