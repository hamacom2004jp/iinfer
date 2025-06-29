from cmdbox.app import app
from iinfer import version


def main(args_list:list=None, webcall:bool=False):
    _app = app.CmdBoxApp.getInstance(appcls=IinferApp, ver=version)
    return _app.main(args_list, webcall=webcall)[0]

class IinferApp(app.CmdBoxApp):
    pass