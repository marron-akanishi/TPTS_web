import os
import sqlite3
import requests
import json

# DBからファイルリスト取得
def get_list(path):
    images = []
    if os.path.exists(path):
        conn = sqlite3.connect(path)
    else:
        raise ValueError
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from list")
    count = cur.fetchone()[0]
    cur.execute( "select * from list order by filename" )
    for row in cur:
        images.append({"id":int(row["filename"]), "tags":row["tags"][1:-1], "image":row["image"]})
    cur.close()
    conn.close()
    return images,count

# DBからIDで検索
def search_db(userid, dbfile):
    images = []
    if os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
    else:
        raise ValueError
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("select count(filename) from list where username like '%" + userid + "%'")
    count = cur.fetchone()[0]
    cur.execute( "select * from list where username like '%" + userid + "%'" )
    for row in cur:
        images.append({"id":int(row["filename"]), "tags":row["tags"][1:-1], "image":row["image"]})
    cur.close()
    conn.close()
    return images,count

# DBから詳細情報取得
def get_detail(filename, dbfile):
    detail = {}
    if os.path.exists(dbfile):
        conn = sqlite3.connect(dbfile)
    else:
        raise ValueError
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
        "tags":row["tags"][1:-1],
        "time":row["time"],
        "facex":row["facex"],
        "facey":row["facey"],
        "facew":row["facew"],
        "faceh":row["faceh"]
    }
    cur.close()
    conn.close()
    temp, idinfo = search_db(detail["userid"], dbfile)
    html = get_html(detail["url"])
    return detail,html,count,idinfo

# 埋め込み用HTMLの取得(detail用)
def get_html(url):
    r = requests.get("https://publish.twitter.com/oembed", {"url":url})
    data = json.loads(r.text)
    try:
        return data["html"]
    except:
        return "error"