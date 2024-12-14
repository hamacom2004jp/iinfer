from cmdbox.app import common, feature
from cmdbox.app.commons import convert, redis_client
from iinfer.app.web import Web
from fastapi import FastAPI, HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect
import gevent
import logging
import json
import queue


class SubImg(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        redis_cli = None
        if not web.client_only:
            redis_cli = redis_client.RedisClient(web.logger, host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname)
        @app.websocket('/webcap/sub_img')
        @app.websocket('/showimg/sub_img')
        async def sub_img(wsock: WebSocket):
            """
            webcap画面又はshowimg画面に対して、web.img_queue又はredisのshowimgに格納された画像を送信する。
            """
            await wsock.accept()
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.sub_img: connected")
            if not wsock:
                raise HTTPException(status_code=400, detail='Expected WebSocket request.')
            while True:
                outputs:dict = None
                try:
                    try:
                        # これを行わねば非同期処理にならない。。
                        await wsock.receive_text()
                        outputs = web.img_queue.get(block=True, timeout=0.001)
                    except queue.Empty:
                        if redis_cli is not None:
                            cmd, outputs = redis_cli.receive_showimg()
                    if outputs is None:
                        gevent.sleep(0.001)
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
                    await wsock.send_text(json.dumps(outputs, default=common.default_json_enc))
                except WebSocketDisconnect:
                    web.logger.warning('web.sub_img: websocket disconnected.')
                    break
                except:
                    if outputs is not None:
                        web.img_queue.put(outputs) # エラーが発生した場合はキューに戻す
                    web.logger.warning('web.start.sub_img:websocket error', exc_info=True)
                    raise HTTPException(status_code=400, detail='Expected WebSocket request.')
