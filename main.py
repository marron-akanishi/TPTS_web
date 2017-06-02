# Flask などの必要なライブラリをインポートする
import os
import glob
from base64 import decodestring
import dbreader
import tweepy
import flask

# 自身の名称を app という名前でインスタンス化する
app = flask.Flask(__name__)
app.secret_key = "konokacyankawaii"

# DB一覧
filelist = []

# Twitter認証用キー
CONSUMER_KEY = "Z0ZmTzB3cmFQdmV0Ym1KbFdqWWcwWHh1Rg=="
CONSUMER_SECRET = "U3RIcEJYaFhFZFhUV09EaUxCVHd0TkFmT3c5TGtKdGJjZzJJOHZYaTVoNkhJeDlPWm4="
CALLBACK_URL = "http://localhost:5000/authed" #実行環境によって変更すること

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    global filelist
    filelist = sorted([path.split(os.sep)[1].split('.')[0] for path in glob.glob("collect/*.db")])
    return flask.render_template('index.html', dblist=filelist, select=filelist[-1])

# aboutページ
@app.route('/about')
def about():
    return flask.render_template('about.html')

# twitter認証ページ
@app.route('/twitter_auth', methods=['GET'])
def twitter_oauth():
    """ 連携アプリ認証用URLにリダイレクト """
    # tweepy でアプリのOAuth認証を行う
    key = decodestring(CONSUMER_KEY.encode("utf8")).decode("ascii")
    secret = decodestring(CONSUMER_SECRET.encode("utf8")).decode("ascii")
    auth = tweepy.OAuthHandler(key, secret, CALLBACK_URL)

    # 連携アプリ認証用の URL を取得
    redirect_url = auth.get_authorization_url()
    # 認証後に必要な request_token を session に保存
    # 辞書型で保管される
    flask.session['request_token'] = auth.request_token

    # リダイレクト
    return flask.redirect(redirect_url)

# twitter認証完了ページ
@app.route('/authed', methods=['GET'])
def twitter_authed():
    return flask.redirect(flask.url_for('index'))

# /list にアクセスしたときの処理
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
                dblist=filelist, select=date, filelist=images, count=count)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# /search にアクセスしたとき
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

# /list/detail にアクセスしたときの処理
@app.route('/list/detail', methods=['GET'])
def image_detail():
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        image_id = flask.request.args.get('id')
        date = flask.request.args.get('date')
        # 画像情報辞書
        try:
            detail,count,idinfo = dbreader.get_detail(int(image_id), "collect/"+date+".db")
        except:
            return flask.render_template('error.html')
        # index.html をレンダリングする
        return flask.render_template('detail.html', 
            data=detail, date=date, max=count, idcount=idinfo)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# 404エラー
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('error.html')

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に