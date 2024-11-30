from cmdbox.app.features.web import cmdbox_web_exec_pipe
from iinfer import version


class ExecPipe(cmdbox_web_exec_pipe.ExecPipe):
    def __init__(self, ver=version):
        super().__init__(ver=ver)
