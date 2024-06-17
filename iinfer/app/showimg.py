from iinfer import version
from iinfer.app.commons import convert
from PIL import Image
from typing import Dict, Any
from pathlib import Path
import copy
import eel
import iinfer
import logging
import queue
import threading

class Showimg(object):
    def __init__(self, logger:logging.Logger, showroot:Path=str(Path(iinfer.__file__).parent / "showroot")):
        self.logger = logger
        eel.init(showroot)
        self.eel_sq = queue.Queue(10)

    def start(self, width:int=1080, height:int=700, web_host:str="localhost", web_port:int=8001):
        self.logger.info(f"Start eel Showimg on http://{web_host}:{web_port}")

        @eel.expose
        def copyright():
            return version.__copyright__

        @eel.expose
        def versions_iinfer():
            return version.__description__.split('\n')
    
        @eel.expose
        def versions_used():
            with open(Path(iinfer.__file__).parent / 'licenses' / 'files.txt', 'r', encoding='utf-8') as f:
                ret = []
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            return ret

        def run_eel(eel_sq:queue.Queue):
            self.showing = True
            eel.js_console_modal_log_func('== console log start ==\n')
            def show_proc():
                while self.showing:
                    try:
                        eel.sleep(0.1)
                        params = eel_sq.get(block=True, timeout=1)
                        outputs:Dict[str, Any] = params[0]
                        output_image:Image.Image = params[1]
                        jpg = convert.img2byte(output_image)
                        jpg_url = f"data:image/jpeg;base64,{convert.bytes2b64str(jpg)}"
                        outputs = copy.deepcopy(outputs)
                        if 'output_image' in outputs:
                            del outputs['output_image']
                        if 'output_image_shape' in outputs:
                            del outputs['output_image_shape']
                        eel.js_show_func(outputs, jpg_url)
                    except queue.Empty:
                        eel.sleep(0.1)
            eel.spawn(show_proc)
            eel.start("showimg.html", size=(width, height), block=False, port=web_port, host=web_host, close_callback=self.stop)
            while self.showing:
                eel.sleep(0.1)
        self.eel_th = threading.Thread(target=run_eel, args=(self.eel_sq,))
        self.eel_th.start()

    def show(self, outputs:Dict[str, Any], output_image:Image.Image):
        self.eel_sq.put((outputs, output_image))

    def stop(self, route, websockets):
        self.showing = False
        exit(0)
