from cmdbox.app.features.web import cmdbox_web_gui
from iinfer import version


class Gui(cmdbox_web_gui.Gui):
    def __init__(self, ver=version):
        super().__init__(ver=ver)
        self.version_info.append(dict(tabid='versions_iinfer', title=version.__appid__,
                                      icon=f'assets/iinfer/icon.png', url='versions_iinfer'))
