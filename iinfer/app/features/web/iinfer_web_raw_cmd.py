from cmdbox.app.features.web import cmdbox_web_raw_cmd
from iinfer import version


class RawCmd(cmdbox_web_raw_cmd.RawCmd):
    def __init__(self, ver=version):
        super().__init__(ver=ver)
