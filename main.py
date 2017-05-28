# Flask などの必要なライブラリをインポートする
import os
import glob
import sqlite3
import flask

# 自身の名称を app という名前でインスタンス化する
app = flask.Flask(__name__)

# DB一覧
filelist = []

# DBからファイルリスト取得
def get_list(path):
    images = []
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from list")
    count = cur.fetchone()[0]
    cur.execute("select * from list")
    for row in cur:
        images.append({"id":int(row["filename"]), "tags":row["tags"][1:-1], "image":row["image"]})
    cur.close()
    conn.close()
    return sorted(images, key=lambda id: id['id']),count

# DBから詳細情報取得
def get_detail(filename, dbfile):
    detail = {}
    if os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
    else:
        return 0,0
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from list")
    count = int(cur.fetchone()[0])-1
    cur.execute( "select * from list where filename = '" + str(filename).zfill(5) + "'" )
    row = cur.fetchone()
    detail = {
        "id":int(row["filename"]),
        "image":row["image"],
        "url":row["url"],
        "userid":row["username"],
        "fav":row["fav"],
        "rt":row["retweet"],
        "tags":row["tags"][1:-1],
        "time":row["time"],
        "facex":row["facex"],
        "facey":row["facey"],
        "facew":row["facew"],
        "faceh":row["faceh"]
    }
    cur.close()
    conn.close()
    return detail,count

# ここからウェブアプリケーション用のルーティングを記述
# index にアクセスしたときの処理
@app.route('/')
def index():
    # index.html をレンダリングする
    global filelist
    filelist = sorted([path.split(os.sep)[1].split('.')[0] for path in glob.glob("collect/*.db")])
    return flask.render_template('index.html', dblist=filelist, select=filelist[-1])

# /list にアクセスしたときの処理
@app.route('/list', methods=['GET', 'POST'])
def image_list():
    global filelist
    if flask.request.method == 'POST':
        # リクエストフォーム取得して
        date = flask.request.form['date']
        # 画像一覧生成
        images,count = get_list("collect/" + date + ".db")
        # index.html をレンダリングする
        return flask.render_template('list.html',
                dblist=filelist, select=date, filelist=images, count=count)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

# /list/detail にアクセスしたときの処理
@app.route('/list/detail', methods=['GET', 'POST'])
def image_detail():
    if flask.request.method == 'GET':
        # リクエストフォーム取得して
        image_id = flask.request.args.get('id')
        date = flask.request.args.get('date')
        # 画像情報辞書
        detail,count = get_detail(int(image_id), "collect/"+date+".db")
        # index.html をレンダリングする
        return flask.render_template('detail.html', data=detail, date=date, max=count)
    else:
        # エラーなどでリダイレクトしたい場合はこんな感じで
        return flask.redirect(flask.url_for('index'))

if __name__ == '__main__':
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0') # どこからでもアクセス可能に