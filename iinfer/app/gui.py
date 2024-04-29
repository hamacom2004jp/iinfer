from iinfer.app import web
from pathlib import Path
import bottle
import eel
import logging
import iinfer


class Gui(web.Web):
    def __init__(self, logger:logging.Logger, data:Path):
        super().__init__(logger, data)
        eel.init(str(Path(iinfer.__file__).parent / "web"))

    def start(self, width:int=1080, height:int=700, web_host:str="localhost", web_port:int=8080):
        self.logger.info(f"Start eel web on http://{web_host}:{web_port}")

        @eel.expose
        def get_mode_opt():
            return self.get_mode_opt()

        @eel.expose
        def get_cmd_opt(mode):
            return self.get_cmd_opt(mode)

        @eel.expose
        def get_opt_opt(mode, cmd):
            return self.get_opt_opt(mode, cmd)

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

        @eel.expose
        def versions_used():
            return self.versions_used()
        
        @bottle.route('/filer/upload', method='POST')
        def filer_upload():
            return self.filer_upload(bottle.request)

        eel.js_console_modal_log_func('== console log start ==\n')
        eel.start("gui.html", size=(width, height), block=True, port=web_port, host=web_host, close_callback=self.stop)

    def callback_console_modal_log_func(self, output:dict):
        eel.js_console_modal_log_func(output)
    
    def callback_return_cmd_exec_func(self, title, output:dict):
        eel.js_return_cmd_exec_func(title, output)

    def callback_return_pipe_exec_func(self, title, output):
        eel.js_return_pipe_exec_func(title, output)

    def stop(self, route, websockets):
        self.bbforce_cmd()
        self.logger.info(f"Stop eel web. {route}")
        exit(0)

