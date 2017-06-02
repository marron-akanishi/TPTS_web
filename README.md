# TPTS web  
Twitterのタイムラインに流れてきた画像から二次元画像だけを自動収集  

## Dockerで使う場合(Host: ArchLinux, Guest: ArchLinux)
localhost:5050にポートフォワードしている。  
/etc/localtimeにバインドして、JST対応  
collect/にoauth.pyを追加しておくこと(下記参照)  
```bash
# docker build -t tpts .
# docker run -d -p 5050:5000 -ti -v /etc/localtime:/etc/localtime:ro tpts
```

## ローカルで使う場合

oauth.pyをcollect/に追加(TwitterのAPIキーを記載)  
```python
# oauth.py
import tweepy as tp

oauth_keys = {
    'CONSUMMER_KEY' : '',
    'CONSUMMER_SECRET' : '',
    'ACCESS_TOKEN_KEY' : '',
    'ACCESS_TOKEN_SECRET' : ''
}

def get_oauth():
    """oauth_keysから各種キーを取得し、OAUTH認証を行う"""
    consumer_key, consumer_secret = \
        oauth_keys['CONSUMMER_KEY'], oauth_keys['CONSUMMER_SECRET']
    access_key, access_secret = \
        oauth_keys['ACCESS_TOKEN_KEY'], oauth_keys['ACCESS_TOKEN_SECRET']
    auth = tp.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    return auth
```

### 必要なツールの導入
#### Debian系の場合
```bash
$ sudo apt install python3 python3-pip python3-venv git cmake gcc libboost-python-dev
```

#### RedHat系の場合
```bash
$ sudo dnf install python3 python3-pip git cmake gcc boost
```

#### ArchLinuxの場合

```bash
# pacman -S python python-pip git cmake gcc boost
```

### 上記の作業で必要なツールを入れた後に以下を実行(Debian系でテスト)
```bash
$ git clone https://github.com/marron-akanishi/TPTS_web
$ cd TPTS_web
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

### スクリプトの実行
#### コレクターの起動
```bash
(venv)$ python3 collect/TL.py
```

#### ビュアーの起動
```bash
(venv)$ python3 main.py
```
