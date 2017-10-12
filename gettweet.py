import os
import time
import datetime
import hashlib
import urllib
import sqlite3
import json
import tweepy as tp
import detector

fileno = 0
file_md5 = []

def reset(dbfile, mode):
    """保存用のフォルダーを生成し、必要な変数を初期化する"""
    try:
        dbfile.execute("drop table result")
    except:
        None
    try:
        dbfile.execute("drop table {}".format(mode))
    except:
        None
    dbfile.execute("vacuum")
    dbfile.execute("create table {} (filename, image, username, url, tags, time, facex, facey, facew, faceh)".format(mode))
    dbfile.execute("create table result (mode, time, image_count, tweet_count)")
    dbfile.commit()

def on_status(status, dbfile, mode):
    """UserStreamから飛んできたStatusを処理する"""
    global fileno
    global file_md5
    # ツイートについてる画像枚数
    image_count = 0
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
                temp_file = urllib.request.urlopen(media_url+":small").read()
            except:
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
                # 取得済みとしてハッシュ値を保存
                file_md5.append(current_md5)
                # ハッシュタグがあれば保存する
                tags = []
                if hasattr(status, "entities"):
                    if "hashtags" in status.entities:
                        for hashtag in status.entities['hashtags']:
                            tags.append(hashtag['text'])
                # データベースに保存
                SQL = "insert into {} values (?,?,?,?,?,?,?,?,?,?)".format(mode)
                url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                value = (filename, media_url, status.user.screen_name, url, str(tags).replace("'",""), 
                        str(datetime.datetime.now()), str(facex), str(facey), str(facew), str(faceh))
                dbfile.execute(SQL, value)
                dbfile.commit()
                fileno += 1
            temp_file = None
            image_count += 1
    return image_count

def getTweets(api, mode, count, query):
    start = time.time()

    dbpath = os.path.abspath(__file__).replace(os.path.basename(__file__),"/DB/user/"+ api.me().id_str + ".db")
    dbfile = sqlite3.connect(dbpath)
    
    # DBのリセット等
    reset(dbfile, mode)
    tweet_count = image_count = 0
    tweet_id = []
    # 取得モード
    if mode == "timeline":
        for status in tp.Cursor(api.home_timeline).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    elif mode == "fav":
        for status in tp.Cursor(api.favorites).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    elif mode == "user":
        for status in tp.Cursor(api.user_timeline, screen_name=query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    elif mode == "list":
        listurl = query.replace("https://","")
        owner = listurl.split("/")[1]
        slug = listurl.split("/")[3]
        for status in tp.Cursor(api.list_timeline, owner_screen_name=owner, slug=slug).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    elif mode == "tag":
        for status in tp.Cursor(api.search, q="#" + query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    elif mode == "keyword":
        for status in tp.Cursor(api.search, q=query).items(count):
            if status.id in tweet_id:
                continue
            else:
                tweet_id.append(status.id)
            image_count += on_status(status, dbfile, mode)
            tweet_count += 1
    
    elapsed_time = time.time() - start
    # 実行時間,全ツイート数,全画像枚数をデータベースに
    SQL = "insert into result values (?,?,?,?)"
    value = (mode, str(elapsed_time), str(image_count), str(tweet_count))
    dbfile.execute(SQL, value)
    dbfile.commit()
        
