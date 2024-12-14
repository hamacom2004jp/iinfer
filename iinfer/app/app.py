from cmdbox.app import app
from iinfer import version


def main(args_list:list=None):
    _app = app.CmdBoxApp.getInstance(appcls=IinferApp, ver=version)
    return _app.main(args_list)[0]

class IinferApp(app.CmdBoxApp):
    pass