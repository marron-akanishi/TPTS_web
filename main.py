# Flask などの必要なライブラリをインポートする
import os
import glob
from base64 import decodestring
import dbreader
import tweepy as tp
import flask

# 自身の名称を app という名前でインスタンス化する
app = flask.Flask(__name__)
# session用のキー
app.secret_key = "konokacyankawaii"

# DB一覧
filelist = []

# Twitter認証用キー
ADMIN_USER = "marron_general"
CONSUMER_KEY = "Z0ZmTzB3cmFQdmV0Ym1KbFdqWWcwWHh1Rg=="
CONSUMER_SECRET = "U3RIcEJYaFhFZFhUV09EaUxCVHd0TkFmT3c5TGtKdGJjZzJJOHZYaTVoNkhJeDlPWm4="
CALLBACK_URL = "http://localhost:5000/authed" #実行環境によって変更すること
auth_temp = None #一時認証情報保存用(これでAPI操作をしないこと)

def get_auth(url=None):
    key = decodestring(CONSUMER_KEY.encode("utf8")).decode("ascii")
    secret = decodestring(CONSUMER_SECRET.encode("utf8")).decode("ascii")
    auth = tp.OAuthHandler(key, secret, url)
    return auth

# 認証後に使用可能
def admin_check():
    auth = get_auth()
    auth.set_access_token(flask.session['key'],flask.session['secret'])
    api = tp.API(auth)
    if api.me().screen_name == ADMIN_USER:
        return True
    else:
        return False

# ここからウェブアプリケーション用のルーティングを記述
# index
@app.route('/')
def index():
    return flask.render_template('index.html')

# about
@app.route('/about')
def about():
    return flask.render_template('about.html')

# twitter認証
@app.route('/twitter_auth', methods=['GET'])
def twitter_oauth():
    # cookieチェック
    key = flask.request.cookies.get('key')
    secret = flask.request.cookies.get('secret')
    if key is None or secret is None:
        global auth_temp
        # tweepy でアプリのOAuth認証を行う
        auth_temp = get_auth(CALLBACK_URL)
        # 連携アプリ認証用の URL を取得
        redirect_url = auth_temp.get_authorization_url()
        # 認証後に必要な request_token を session に保存
        flask.session['request_token'] = auth_temp.request_token
        # リダイレクト
        return flask.redirect(redirect_url)
    else:
        flask.session['key'] = key
        flask.session['secret'] = secret
        return flask.redirect(flask.url_for('twitter_authed', cookie=True))

# twitter認証完了
@app.route('/authed', methods=['GET'])
def twitter_authed():
    # 認証情報取得
    if flask.request.args.get('cookie') != "True":
        global auth_temp
        auth_temp.request_token = flask.session['request_token']
        auth_temp.get_access_token(flask.request.args.get('oauth_verifier'))
        flask.session['key'] = auth_temp.access_token
        flask.session['secret'] = auth_temp.access_token_secret
        flask.session['request_token'] = None
        auth_temp = None
    # 認証ユーザー取得
    if admin_check:
        response = flask.make_response(flask.redirect(flask.url_for('admin_page')))
        response.set_cookie('key', flask.session['key'])
        response.set_cookie('secret', flask.session['secret'])
        return response
    else:
        response = flask.make_response(flask.redirect(flask.url_for('user_page')))
        response.set_cookie('key', flask.session['key'])
        response.set_cookie('secret', flask.session['secret'])
        return response

# admin
@app.route('/admin')
def admin_page():
    if admin_check == False:
        return flask.render_template('error.html')
    global filelist
    filelist = sorted([path.split(os.sep)[1].split('.')[0] for path in glob.glob("collect/*.db")])
    return flask.render_template('admin.html', dblist=filelist, select=filelist[-1], authed=True)

# user
@app.route('/user')
def user_page():
    return flask.render_template('user.html')

# 共通ページ
# list
@app.route('/list', methods=['GET'])
def image_list():
    global filelist
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        date = flask.request.args.get('date')
        # 画像一覧生成
        try:
            images,count = dbreader.get_list("collect/" + date + ".db")
        except:
            return flask.render_template('error.html')
        # index.html をレンダリングする
        return flask.render_template('list.html',
                dblist=filelist, select=date, filelist=images, count=count, admin=admin_check())
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# search
@app.route('/search', methods=['GET'])
def image_search():
    global filelist
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        date = flask.request.args.get('date')
        userid = flask.request.args.get('userid')
        # 画像一覧生成
        try:
            images,count = dbreader.search_db(userid, "collect/" + date + ".db")
        except:
            return flask.render_template('error.html')
        # index.html をレンダリングする
        return flask.render_template('list.html',
                dblist=filelist, select=date, filelist=images, count=count)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# /list/detail
@app.route('/list/detail', methods=['GET'])
def image_detail():
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        image_id = flask.request.args.get('id')
        date = flask.request.args.get('date')
        # 画像情報
        try:
            detail,html,count,idinfo = dbreader.get_detail(int(image_id), "collect/"+date+".db")
        except:
            return flask.render_template('error.html')
        # index.html をレンダリングする
        return flask.render_template('detail.html', 
            data=detail, html=html, date=date, max=count, idcount=idinfo)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# 404エラー
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error.html')

if __name__ == '__main__':
    app.debug = True # デバッグモード
    app.run(host='0.0.0.0') # どこからでもアクセス可能に