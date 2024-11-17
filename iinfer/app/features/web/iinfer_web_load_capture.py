from iinfer.app import common, web, feature
from iinfer.app.commons import convert
from typing import List, Dict, Any
from pathlib import Path
import bottle
import json
import logging


class LoadCapture(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/gui/load_capture', method='POST')
        def load_capture():
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            current_path = bottle.request.forms.get('current_path')
            ret = self.load_capture(web, current_path)
            bottle.response.content_type = 'application/json'
            return json.dumps(ret, default=common.default_json_enc)

    def load_capture(self, web:web.Web, current_path:str) -> List[Dict[str, Any]]:
        """
        キャプチャファイルを読み込む

        Args:
            web (web.Web): Webオブジェクト
            current_path (str): カレントパス

        Returns:
            list[Dict[str, Any]]: キャプチャファイルの内容
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_capture: current_path={current_path}")
        current_path = Path(current_path)
        if not current_path.is_file():
            return {'warn': f'A non-file was selected.: {current_path}'}
        try:
            with open(current_path, 'r', encoding='utf-8') as f:
                ret = []
                for line in f:
                    cel = line.split(',')
                    res_json = dict(success=dict(image_name=cel[5]),
                                    output_image=None,
                                    output_image_shape=(int(cel[2]),int(cel[3]),int(cel[4])),
                                    output_image_name=cel[5])
                    if cel[0] == 'capture':
                        img_npy = convert.b64str2npy(cel[1], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='jpeg')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                    else:
                        res_json["output_image"] = cel[1]
                    ret.append(res_json)
                return ret
        except:
            return {'warn': f'An error occurred while reading the file.: {current_path}'}
    