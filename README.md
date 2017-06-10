# TPTS web  
Twitterから二次元画像を効率よく回収しよう！  

### 現在わかっているバグ

- デバッグモードでFlask内蔵サーバーを使って走らせると収集スクリプトが二重に走る  
- 画像の判定が遅い  
- 判定の精度が低い

## Dockerで使う場合(Host: ArchLinux, Guest: ArchLinux)
localhost:5050にポートフォワードしている。  
/etc/localtimeにバインドして、JST対応  
setting.jsonを追加しておくこと(下記参照)  
```bash
# docker build -t tpts .
# docker run -d -p 5050:5000 -ti -v /etc/localtime:/etc/localtime:ro tpts
```

## ローカルで使う場合

setting_empty.jsonをsetting.jsonに変更(設定を記載)  
設定を以下の通り 
```json
{
    "SecretKey": "Sessionを保存する際に使用するキー(ランダム文字列)",
    "AdminID": "管理者となるユーザーのTwitterID",
    "twitter_API": {
        "CK": "TwitterAPI(ConsumerKey)",
        "CS": "TwitterAPI(ConsumerSecret)",
        "Admin_Key": "管理者のAccessToken(API管理ページで生成)",
        "Admin_Secret": "管理者のAccessTokenSecret",
        "Callback_URL": "http://{運営するドメイン}/authed(API管理ページでも指定)"
    },
    "MaxCount": "一回で取得するツイート数(大きいと時間もリソースも食うので初期設定をおすすめします,100ずつ指定)",
    "AdminShow": "管理者以外も管理者アカウントで回収した画像を見れるようにするかどうか",
    "Debug": "デバッグモード"
}
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
```bash
(venv)$ python3 app.py
```
