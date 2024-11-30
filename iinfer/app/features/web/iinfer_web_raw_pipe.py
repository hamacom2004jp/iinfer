from cmdbox.app.features.web import cmdbox_web_raw_pipe
from iinfer import version


class RawPipe(cmdbox_web_raw_pipe.RawPipe):
    def __init__(self, ver=version):
        super().__init__(ver=ver)
