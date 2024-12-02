from cmdbox.app.app import CmdBoxApp
from iinfer import version


def main(args_list:list=None):
    app = IinferApp.getInstance()
    return app.main(args_list)[0]

class IinferApp(CmdBoxApp):
    _instance = None
    @staticmethod
    def getInstance():
        if IinferApp._instance is None:
            IinferApp._instance = IinferApp()
        return IinferApp._instance

    def __init__(self):
        super().__init__(ver=version,
                         cli_features_packages=['iinfer.app.features.cli'], cli_features_prefix=['iinfer_'])
