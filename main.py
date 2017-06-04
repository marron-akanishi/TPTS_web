# Flask などの必要なライブラリをインポートする
import os
import glob
import json
import DBreader as db
import tweepy as tp
import flask
from functools import wraps

# 自身の名称を app という名前でインスタンス化する
app = flask.Flask(__name__)
setting = json.load(open("setting.json"))

# DB一覧
filelist = []

# 認証後に使用可能
def tp_api():
    auth = tp.OAuthHandler(setting['twitter_API']['CK'], setting['twitter_API']['CS'], setting['twitter_API']['Callback_URL'])
    auth.set_access_token(flask.session['key'],flask.session['secret'])
    return tp.API(auth)

def admin_check():
    return flask.session['name'] == setting['AdminID']

def login_check(func):
    @wraps(func)
    def checker(*args, **kwargs):
        # きちんと認証していればセッション情報がある
        try:
            if flask.session['userID'] is None:
                return flask.redirect(flask.url_for('index'))
        except:
            return flask.redirect(flask.url_for('index'))
        return func(*args, **kwargs)
    return checker

# ここからウェブアプリケーション用のルーティングを記述
# トップページ
@app.route('/')
def index():
    key = flask.request.cookies.get('key')
    secret = flask.request.cookies.get('secret')
    if key is None or secret is None:
        return flask.render_template('index.html')
    else:
        flask.session['key'] = key
        flask.session['secret'] = secret
        return flask.redirect(flask.url_for('twitter_authed', cookie=True))

# twitter認証
@app.route('/twitter_auth', methods=['GET'])
def twitter_oauth():
    # cookieチェック
    key = flask.request.cookies.get('key')
    secret = flask.request.cookies.get('secret')
    if key is None or secret is None:
        # tweepy でアプリのOAuth認証を行う
        auth_temp = tp.OAuthHandler(setting['twitter_API']['CK'], setting['twitter_API']['CS'], setting['twitter_API']['Callback_URL'])
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
        auth_temp = tp.OAuthHandler(setting['twitter_API']['CK'], setting['twitter_API']['CS'], setting['twitter_API']['Callback_URL'])
        auth_temp.request_token = flask.session['request_token']
        auth_temp.get_access_token(flask.request.args.get('oauth_verifier'))
        flask.session['key'] = auth_temp.access_token
        flask.session['secret'] = auth_temp.access_token_secret
        flask.session['request_token'] = None
    # 認証ユーザー取得
    flask.session['name'] = tp_api().me().screen_name
    flask.session['userID'] = tp_api().me().id_str
    response = flask.make_response(flask.redirect(flask.url_for('user_page')))
    response.set_cookie('key', flask.session['key'])
    response.set_cookie('secret', flask.session['secret'])
    return response

# ログアウトボタン
@app.route('/logout')
def logout():
    response = flask.make_response(flask.redirect(flask.url_for('index')))
    response.set_cookie('key', '', expires=0)
    response.set_cookie('secret', '', expires=0)
    flask.session.clear()
    return response

# こっから下は認証が必要
# ユーザーメニュー
@app.route('/user')
@login_check
def user_page():
    return flask.render_template('user.html', admin=admin_check(), showadminTL=setting['AdminShow'])

# モード切り替え
@app.route('/user/<mode>')
@login_check
def user_getter(mode):
    if mode == "admin":
        if admin_check() or setting['AdminShow']:
            global filelist
            filelist = sorted([path.split(os.sep)[1].split('.')[0] for path in glob.glob("DB/admin/*.db")])
            return flask.render_template('mode.html', mode=mode, dblist=filelist, select=filelist[-1])
        else:
            return flask.render_template('user.html')
    return flask.render_template('mode.html', mode=mode)

# ログページ
@app.route('/user/admin/logs')
@login_check
def log_page():
    return

# 共通ページ
# 画像リストビュー生成
@app.route('/getlist', methods=['POST'])
@login_check
def image_list():
    date = 0
    mode = flask.request.form['mode']
    if mode == "homeTL":
        pass
    elif mode == "userTL":
        pass
    elif mode == "list":
        pass
    elif mode == "admin":
        if admin_check() == False or setting['AdminShow'] == False:
                return flask.render_template('error.html')
        date = flask.request.form['date']
        try:
            images,count = db.get_list("DB/admin/" + date + ".db")
        except:
            return flask.render_template('error.html')
    return flask.render_template('list.html', filelist=images, select=date, count=count, mode=mode, userID=flask.session['userID'])

# 検索結果生成
@app.route('/search', methods=['GET'])
@login_check
def image_search():
    global filelist
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        date = flask.request.args.get('date')
        userid = flask.request.args.get('userid')
        # 画像一覧生成
        try:
            images,count = db.search_db(userid, "collect/" + date + ".db")
        except:
            return flask.render_template('error.html')
        # index.html をレンダリングする
        return flask.render_template('list.html', dblist=filelist, select=date, filelist=images, count=count)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# 画像詳細
@app.route('/detail', methods=['GET'])
@login_check
def image_detail():
    if flask.request.method == 'GET':
        mode = flask.request.args.get('mode')
        userid = flask.request.args.get('user')
        image_id = flask.request.args.get('id')
        # ログインIDチェック
        if userid != flask.session['userID']:
            return flask.render_template('error.html')
        if mode == "admin":
            if admin_check() == False or setting['AdminShow'] == False:
                return flask.render_template('error.html')
            date = flask.request.args.get('date')
            try:
                detail,html,count,idinfo = db.get_detail(int(image_id), "DB/admin/"+date+".db")
            except:
                return flask.render_template('error.html')
        else:
            pass
        # index.html をレンダリングする
        return flask.render_template('detail.html', 
            data=detail, html=html, date=date, max=count, idcount=idinfo)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# 認証不要ページ
# このページについて
@app.route('/about')
def about():
    return flask.render_template('about.html')

# 404エラー
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error.html')

if __name__ == '__main__':
    app.secret_key = setting['SecretKey']
    app.debug = setting['Debug'] # デバッグモード
    app.run(host='0.0.0.0') # どこからでもアクセス可能に