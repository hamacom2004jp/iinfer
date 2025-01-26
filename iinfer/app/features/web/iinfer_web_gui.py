from cmdbox.app.features.web import cmdbox_web_gui
from iinfer import version


class Gui(cmdbox_web_gui.Gui):
    def __init__(self, appcls, ver):
        super().__init__(appcls, ver)
        self.version_info.append(dict(tabid='versions_iinfer', title=version.__appid__,
                                      thisapp=True if version.__appid__ == ver.__appid__ else False,
                                      icon=f'assets/iinfer/icon.png', url='versions_iinfer'))
