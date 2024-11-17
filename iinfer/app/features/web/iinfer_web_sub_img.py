from iinfer.app import common, web, feature
from iinfer.app.commons import convert, redis_client
import bottle
import gevent
import logging
import json
import queue
import time
import traceback


class SubImg(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        redis_cli = None
        if not web.client_only:
            redis_cli = redis_client.RedisClient(web.logger, host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname)
        @app.route('/webcap/sub_img')
        @app.route('/showimg/sub_img')
        def sub_img():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            wsock = bottle.request.environ.get('wsgi.websocket') # type: ignore
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.sub_img: connected")
            if not wsock:
                bottle.abort(400, 'Expected WebSocket request.')
            while True:
                outputs:dict = None
                try:
                    try:
                        outputs = web.img_queue.get(block=True, timeout=0.001)
                    except queue.Empty:
                        if redis_cli is not None:
                            cmd, outputs = redis_cli.receive_showimg()
                    if outputs is None:
                        gevent.sleep(0.1)
                        continue
                    outputs['outputs_key'] = web.outputs_key
                    if outputs['outputs_key'] is None or len(outputs['outputs_key']) <= 0:
                        def _get_outputs_key(src:dict, dst:list):
                            for key in src.keys():
                                if isinstance(src[key], dict):
                                    _get_outputs_key(src[key], dst)
                                else:
                                    dst.append(key)
                        outputs_key = []
                        _get_outputs_key(outputs['success'], outputs_key)
                        outputs['outputs_key'] = list(set(outputs_key))
                    if web.logger.level == logging.DEBUG:
                        output_str = common.to_str(outputs, slise=100)
                        web.logger.debug(f"web.sub_img: outputs_key={outputs['outputs_key']}, output_str={output_str}")
                    if 'output_image_shape' in outputs:
                        img_npy = convert.b64str2npy(outputs["output_image"], outputs["output_image_shape"])
                        jpg = convert.img2byte(convert.npy2img(img_npy), format='jpeg')
                        jpg_url = f"data:image/jpeg;base64,{convert.bytes2b64str(jpg)}"
                        del outputs["output_image"]
                        del outputs["output_image_shape"]
                        outputs['img_url'] = jpg_url
                        outputs['img_id'] = outputs['output_image_name'].strip()
                    elif type(outputs) == tuple:
                        fn = outputs[0]
                        jpg_url = f"data:image/jpeg;base64,{convert.bytes2b64str(outputs[1])}"
                        outputs = dict(output_image_name=fn)
                        outputs['img_url'] = jpg_url
                        outputs['img_id'] = fn
                    wsock.send(json.dumps(outputs, default=common.default_json_enc))
                except:
                    if outputs is not None:
                        web.img_queue.put(outputs) # エラーが発生した場合はキューに戻す
                    web.logger.warning('web.start.sub_img:websocket error', exc_info=True)
                    bottle.abort(400, 'Expected WebSocket request.')
                    return
