import os
import datetime
import hashlib
import urllib
import sqlite3
import json
import urllib.request
from bs4 import BeautifulSoup
import tweepy as tp
import detector

fileno = 0
file_hash = []
file_md5 = []
dbfile = None

def reset(filename):
    """保存用のフォルダーを生成し、必要な変数を初期化する"""
    global dbfile
    dbpath = os.path.abspath(__file__).replace(os.path.basename(__file__),"/DB/user/"+ filename + ".db")
    dbfile = sqlite3.connect(dbpath)
    try:
        dbfile.execute("drop table list")
        dbfile.execute("vacuum")
    except:
        None
    dbfile.execute("create table list (filename, image, username, url, tags, time, facex, facey, facew, faceh)")

def on_status(status):
    """UserStreamから飛んできたStatusを処理する"""
    global fileno
    global file_hash
    global file_md5
    # Tweetに画像がついているか
    is_media = False
    # TweetがRTかどうか
    if hasattr(status, "retweeted_status"):
        status = status.retweeted_status
    # Tweetが引用ツイートかどうか
    if hasattr(status, "quoted_status"):
        status = status.quoted_status
    # 複数枚の画像ツイートのとき
    if hasattr(status, "extended_entities"):
        if 'media' in status.extended_entities:
            status_media = status.extended_entities
            is_media = True
    # 一枚の画像ツイートのとき
    elif hasattr(status, "entities"):
        if 'media' in status.entities:
            status_media = status.entities
            is_media = True

    # 画像がついていたとき
    if is_media:
        for image in status_media['media']:
            if image['type'] != 'photo':
                break
            # URL, ファイル名
            media_url = image['media_url']
            filename = str(fileno).zfill(5)
            # ダウンロード
            try:
                temp_file = urllib.request.urlopen(media_url).read()
            except:
                print("Download Error")
                continue
            # md5の取得
            current_md5 = hashlib.md5(temp_file).hexdigest()
            # すでに取得済みの画像は飛ばす
            if current_md5 in file_md5:
                continue
            # 画像判定呼出
            current_hash = None
            current_hash, facex, facey, facew, faceh = detector.face_2d(temp_file, status.user.screen_name, filename)
            if current_hash is not None:
                # すでに取得済みの画像は飛ばす
                overlaped = False
                for hash_key in file_hash:
                    check = int(hash_key,16) ^ int(current_hash,16)
                    count = bin(check).count('1')
                    if count < 7:
                        overlaped = True
                        break
                # 画像情報保存
                if overlaped != True:
                    # 取得済みとしてハッシュ値を保存
                    file_hash.append(current_hash)
                    file_md5.append(current_md5)
                    # ハッシュタグがあれば保存する
                    tags = []
                    if hasattr(status, "entities"):
                        if "hashtags" in status.entities:
                            for hashtag in status.entities['hashtags']:
                                tags.append(hashtag['text'])
                    # データベースに保存
                    url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                    dbfile.execute("insert into list(filename) values('" + filename + "')")
                    dbfile.execute("update list set image = '" + media_url + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set username = '" + status.user.screen_name + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set url = '" + url + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set tags = '" + str(tags).replace("'","") + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set time = '" + str(datetime.datetime.now()) + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set facex = '" + str(facex) + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set facey = '" + str(facey) + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set facew = '" + str(facew) + "' where filename = '" + filename + "'")
                    dbfile.execute("update list set faceh = '" + str(faceh) + "' where filename = '" + filename + "'")
                    dbfile.commit()
                    fileno += 1
            temp_file = None

def start(api, listurl):
    """メイン関数"""
    start = 1
    reset(api.me().id_str)
    # URLからHTMLをパースする
    req = urllib.request.Request(listurl, headers={'User-Agent' : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"}) 
    con = urllib.request.urlopen(req)
    soup = BeautifulSoup(con, "html.parser")
    listid = soup.find('div',{'class':'follow-card'}).get('data-list-id')
    owner = soup.find('a',{'class':'list-author'}).get('href')[1:]
    for i in range(0,2):
        for status in api.list_timeline(owner=owner,slug=listid,since_id=start,count=200):
            on_status(status)
            start = status.id