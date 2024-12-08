from cmdbox.app.features.web import cmdbox_web_exec_cmd
from fastapi import Request, Response
from iinfer import version
from iinfer.app import app
from iinfer.app.web import Web
from typing import Dict, Any, List


class ExecCmd(cmdbox_web_exec_cmd.ExecCmd):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def exec_cmd(self, req:Request, res:Response, web:Web, title:str, opt:Dict[str, Any], nothread:bool=False, appcls=app.IinferApp) -> List[Dict[str, Any]]:
        """
        コマンドを実行する

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
            web (Web): Webオブジェクト
            title (str): タイトル
            opt (dict): オプション
            nothread (bool, optional): スレッドを使わないかどうか. Defaults to False.
        
        Returns:
            list: コマンド実行結果
        """
        return super().exec_cmd(req, res, web, title, opt, nothread, appcls)
