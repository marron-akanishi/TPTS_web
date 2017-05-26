# printで表示する状態情報は半角6文字以内にすること

import os
import time
import datetime
import hashlib
import urllib
import sqlite3
import tweepy as tp
import detector
import oauth

class StreamListener(tp.StreamListener):
    def __init__(self, api):
        """コンストラクタ"""
        self.api = api
        # 保存先
        self.old_date = datetime.date.today()
        self.reset()

    def on_status(self, status):
        """UserStreamから飛んできたStatusを処理する"""
        # Tweetに画像がついているか
        is_media = False
        # 日付の確認
        now = datetime.date.today()
        if now != self.old_date:
            self.old_date = now
            self.dbfile.commit()
            self.dbfile.close()
            self.reset()
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
            # 自分のツイートは飛ばす
            if status.user.screen_name != "marron_general" and status.user.screen_name != "marron_recbot":
                for image in status_media['media']:
                    if image['type'] != 'photo':
                        break
                    # URL, ファイル名
                    media_url = image['media_url']
                    filename = str(self.fileno).zfill(5)
                    # ダウンロード
                    try:
                        temp_file = urllib.request.urlopen(media_url).read()
                    except:
                        print("Download Error")
                        continue
                    # md5の取得
                    current_md5 = hashlib.md5(temp_file).hexdigest()
                    # すでに取得済みの画像は飛ばす
                    if current_md5 in self.file_md5:
                        print("geted  : " + status.user.screen_name +"-" + filename)
                        continue
                    # 画像判定呼出
                    self.all += 1
                    current_hash = None
                    current_hash, facex, facey, facew, faceh = detector.face_2d(temp_file, status.user.screen_name, filename)
                    if current_hash is not None:
                        # すでに取得済みの画像は飛ばす
                        overlaped = False
                        for hash_key in self.file_hash:
                            check = int(hash_key,16) ^ int(current_hash,16)
                            count = bin(check).count('1')
                            if count < 7:
                                print("geted  : " + status.user.screen_name +"-" + filename)
                                overlaped = True
                                break
                        # 画像情報保存
                        if overlaped != True:
                            # 取得済みとしてハッシュ値を保存
                            self.file_hash.append(current_hash)
                            self.file_md5.append(current_md5)
                            # ハッシュタグがあれば保存する
                            tags = []
                            if hasattr(status, "entities"):
                                if "hashtags" in status.entities:
                                    for hashtag in status.entities['hashtags']:
                                        tags.append(hashtag['text'])
                            # データベースに保存
                            url = "https://twitter.com/" + status.user.screen_name + "/status/" + status.id_str
                            self.dbfile.execute("insert into list(filename) values('" + filename + "')")
                            self.dbfile.execute("update list set image = '" + media_url + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set username = '" + status.user.screen_name + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set url = '" + url + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set fav = " + str(status.favorite_count) + " where filename = '" + filename + "'")
                            self.dbfile.execute("update list set retweet = " + str(status.retweet_count) + " where filename = '" + filename + "'")
                            self.dbfile.execute("update list set tags = '" + str(tags)[1:-1].replace("'","") + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set time = '" + str(datetime.datetime.now()) + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set facex = '" + str(facex) + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set facey = '" + str(facey) + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set facew = '" + str(facew) + "' where filename = '" + filename + "'")
                            self.dbfile.execute("update list set faceh = '" + str(faceh) + "' where filename = '" + filename + "'")
                            self.dbfile.commit()
                            print("saved  : " + status.user.screen_name + "-" + filename)
                            if tags != []:
                                print("  tags : " + str(tags))
                            self.fileno += 1
                    temp_file = None

    def reset(self):
        """保存用のフォルダーを生成し、必要な変数を初期化する"""
        self.fileno = 0
        self.all = 0
        self.file_hash = []
        self.file_md5 = []
        self.dbfile = sqlite3.connect(os.path.abspath(__file__).replace(os.path.basename(__file__),self.old_date.isoformat() + ".db"))
        try:
            self.dbfile.execute("create table list (filename, image, username, url, fav, retweet, tags, time, facex, facey, facew, faceh)")
        except:
            None

def main():
    """メイン関数"""
    auth = oauth.get_oauth()
    stream = tp.Stream(auth, StreamListener(tp.API(auth)), secure=True)
    print('Start Streaming!')
    while True:
        try:
            stream.userstream()
        except KeyboardInterrupt:
            exit()
        except:
            print('UserStream Error')
            time.sleep(60)

if __name__ == '__main__':
    main()
