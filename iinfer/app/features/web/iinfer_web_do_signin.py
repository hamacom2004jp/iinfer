from iinfer.app import web, feature
import bottle
import hashlib


class DoSignin(feature.WebFeature):
    def __init__(self):
        super().__init__()
    
    def route(self, web:web.Web, app:bottle.Bottle) -> None:
        @app.route('/signin/<next>', method='POST')
        def do_signin(next):
            userid = bottle.request.forms.get('userid')
            passwd = bottle.request.forms.get('password')
            if userid == '' or passwd == '':
                bottle.redirect(f'/signin/{next}?error=1')
                return
            web.load_signin_file()
            if userid not in web.signin_file_data:
                bottle.redirect(f'/signin/{next}?error=1')
                return
            algname = web.signin_file_data[userid]['algname']
            if algname != 'plain':
                h = hashlib.new(algname)
                h.update(passwd.encode('utf-8'))
                passwd = h.hexdigest()
            if passwd != web.signin_file_data[userid]['password']:
                bottle.redirect(f'/signin/{next}?error=1')
                return
            session = bottle.request.environ.get('beaker.session')
            session['signin'] = dict(userid=userid, password=passwd)
            session.save()
            bottle.redirect(f'/{next}')
