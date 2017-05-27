# TPTS web

## Dockerで使う場合(Host: ArchLinux, Gest: ArchLinux)
localhost:5050にポートフォワードしている。
/etc/localtimeにバインドして、JST対応
```bash
# docker build -t tpts .
# docker run -d -p 5050:5000 -ti -v /etc/localtime:/etc/localtime:ro tpts
```

## ローカルで使う場合

oauth.pyをcollect/に追加
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


### Debian系の場合
```bash
$ sudo apt install python3 python3-pip git cmake gcc boost
```

### RedHat系の場合
```bash
$ sudo dnf install python3 python3-pip git cmake gcc boost
```

### ArchLinuxの場合

```bash
# pacman -S python python-pip git cmake gcc boost
```


```bash
$ git clone https://github.com/guni973/TPTS_web
$ cd TPTS_web
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ sudo pip install -r requirements.txt
```

#### コレクターの起動
```bash
(venv)$ python3 collect/TL.py
```

#### ビュアーの起動
```bash
(venv)$ python3 main.ts
```
