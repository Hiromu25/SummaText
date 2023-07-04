# SummaText

## 事前準備

### poetryのインストール

`curl -sSL https://install.python-poetry.org | python3 -`

[参考URL](https://qiita.com/ksato9700/items/b893cf1db83605898d8a)

### GCPの設定

1. GCPのプロジェクトを作成
2. Cloud Vision APIの有効化
3. Fire Storeの有効化
4. サービスアカウントキーの作成

権限は面倒なので，とりあえずOwnerにしておけば全て動作する

5. 作成したサービスアカウントキーをディレクトリ直下に配置

### Slackアプリの作成

#### Event Subscriptionの設定

subscribe bot eventにおいて，

* message.channels
* message.im
を有効化する

※ 実行方法（ローカル）の5を実行しないと有効化できないことに注意

[参考URL](https://qiita.com/Hiromu25/items/527b49eb3e5541ae7326#2-slackapp%E3%81%AE%E4%BD%9C%E6%88%90)

### Open AIのAPIキーを作成

[参考URL](https://qiita.com/Hiromu25/items/527b49eb3e5541ae7326#1-openai%E3%81%AEapi%E3%82%AD%E3%83%BC%E3%81%AE%E5%8F%96%E5%BE%97)

### 環境変数の設定

`.env`を`.env.example`を参考に作成

## 実行方法(ローカル)

1. `poetry install`
2. `poetry shell`
3. `python main.py`
4. `ngrok http 3000`
5. `生成されたURL/slack/event`をSlackAppのEvent SubscriptionsのRequest URLに設定する

初回起動の場合は以下の処理も実行

7. `生成されたURL/slack/oauth_redirect`をSlackAppのOAuth&PermissionsのRedirect URLsに追加する
8. `生成されたURL/slack/install`にアクセスし，利用したいワークスペースにアプリをインストールする

## デプロイ方法(GCP)

1. `gcloud config set project <自身のPROJECT_ID>`
2. deploy.shの1行目のPROJECT_IDを自身のプロジェクトに変更
3. `sh deploy.sh`
4. Cloud Runにアプリがデプロイされる
