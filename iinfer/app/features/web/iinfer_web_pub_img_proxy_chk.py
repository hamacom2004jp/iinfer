from iinfer.app import common, web, feature
import bottle


class PubImgProxyChk(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/webcap/pub_img/<port:int>', method='GET')
        def pub_img_proxy_chk(port:int):
            if not web.check_signin():
                return common.to_str(dict(warn=f'Please log in to retrieve session.'))
            try:
                # 事前に接続テストすることで、keepaliveを有効にしておく（画像送信時のTCP接続が高速化できる）
                responce = web.webcap_client.get(f'http://localhost:{port}/webcap/pub_img')
                return "ok"
            except:
                return "ng"
