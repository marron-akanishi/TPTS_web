# Flask などの必要なライブラリをインポートする
import glob
import sqlite3
import flask

# 自身の名称を app という名前でインスタンス化する
app = flask.Flask(__name__)

# DB一覧
filelist = [path.split('\\')[1].split('.')[0] for path in glob.glob("collect/*.db")]

# DBからファイルリスト取得
def get_list(path):
    images = []
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute( "select * from list" )
    for row in cur:
        images.append({"id":row["filename"], "url":row["image"]})
    cur.close()
    conn.close()
    return images

# DBから詳細情報取得
def get_detail(filename, dbfile):
    detail = {}
    conn = sqlite3.connect(dbfile)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute( "select * from list where filename = '" + filename + "'" )
    for row in cur:
        detail = {
            "id":row["filename"],
            "image":row["image"],
            "url":row["url"],
            "userid":row["username"],
            "fav":row["fav"],
            "rt":row["retweet"],
            "tags":row["tags"],
            "time":row["time"]
        }
    cur.close()
    conn.close()
    return detail

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    return flask.render_template('index.html', dblist=filelist)

# /list にアクセスしたときの処理
@app.route('/list', methods=['GET', 'POST'])
def image_list():
    if flask.request.method == 'POST':
        # リクエストフォームから「名前」を取得して
        date = flask.request.form['date']
        # 画像一覧生成
        images = get_list("collect/" + date + ".db")
        # index.html をレンダリングする
        return flask.render_template('list.html',
                dblist=filelist, select=date, filelist=images)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# /detail にアクセスしたときの処理
@app.route('/list/detail', methods=['GET', 'POST'])
def image_detail():
    if flask.request.method == 'POST':
        # リクエストフォームから「名前」を取得して
        image_id = flask.request.form['open']
        date = flask.request.form['date']
        # 画像情報辞書
        detail = get_detail(image_id, "collect/"+date+".db")
        # index.html をレンダリングする
        return flask.render_template('detail.html', data=detail)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に