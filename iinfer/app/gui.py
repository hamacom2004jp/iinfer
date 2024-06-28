from iinfer.app import web
from pathlib import Path
import bottle
import eel
import logging
import iinfer
import json

class Gui(web.Web):
    def __init__(self, logger:logging.Logger, data:Path):
        super().__init__(logger, data)
        eel.init(str(Path(iinfer.__file__).parent / "web"))

    def start(self, width:int=1080, height:int=700, web_host:str="localhost", web_port:int=8080):
        self.logger.info(f"Start eel web on http://{web_host}:{web_port}")

        @eel.expose
        def get_local_data():
            return str(self.data)

        @eel.expose
        def get_modes():
            return self.get_modes()

        @eel.expose
        def get_cmds(mode):
            return self.get_cmds(mode)

        @eel.expose
        def get_cmd_choices(mode, cmd):
            return self.get_cmd_choices(mode, cmd)

        @eel.expose
        def list_cmd(kwd):
            return self.list_cmd(kwd)

        @eel.expose
        def save_cmd(title, opt):
            return self.save_cmd(title, opt)

        @eel.expose
        def load_cmd(title):
            return self.load_cmd(title)

        @eel.expose
        def del_cmd(title):
            self.del_cmd(title)

        @eel.expose
        def bbforce_cmd():
            self.bbforce_cmd()

        @eel.expose
        def exec_cmd(title, opt, nothread=False):
            return self.exec_cmd(title, opt, nothread)

        @eel.expose
        def raw_cmd(title, opt):
            return self.raw_cmd(title, opt)

        @eel.expose
        def list_tree(current_path):
            return self.list_tree(current_path)
        
        @eel.expose
        def load_result(current_path):
            return self.load_result(current_path)

        @eel.expose
        def load_capture(current_path):
            return self.load_capture(current_path)

        @eel.expose
        def list_pipe(kwd):
            return self.list_pipe(kwd)

        @eel.expose
        def exec_pipe(title, opt):
            return self.exec_pipe(title, opt)

        @eel.expose
        def raw_pipe(title, opt):
            return self.raw_pipe(title, opt)

        @eel.expose
        def save_pipe(title, opt):
            return self.save_pipe(title, opt)

        @eel.expose
        def del_pipe(title):
            self.del_pipe(title)

        @eel.expose
        def load_pipe(title):
            return self.load_pipe(title)

        @eel.expose
        def copyright():
            return self.copyright()

        @eel.expose
        def versions_iinfer():
            return self.versions_iinfer()

        @bottle.route('/gui/versions_used')
        def versions_used():
            bottle.response.content_type = 'application/json'
            return json.dumps(self.versions_used())
        
        @bottle.route('/filer/upload', method='POST')
        def filer_upload():
            return self.filer_upload(bottle.request)

        @bottle.route('/gui/callback')
        def gui_callback():
            return self.gui_callback()

        @bottle.route('/gui/get_local_data')
        def get_local_data():
            return str(self.data)

        self.callback_console_modal_log_func('== console log start ==\n')
        eel.start("gui.html", size=(width, height), block=True, port=web_port, host=web_host, close_callback=self.stop)

    def stop(self, route, websockets):
        self.bbforce_cmd()
        self.logger.info(f"Stop eel web. {route}")
        exit(0)

