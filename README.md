# article-summarize-bot

## 事前準備

- poetryのインストール
- Cloud Visionの作成
- Fire Storeの作成
- `.env`を`.env.example`を参考に作成

## 実行方法(ローカル)

1. `poetry install`
2. `poetry shell`
3. `python main.py`

## デプロイ方法(GCP)

1. `gcloud config set project <自身のPROJECT_ID>`
2. deploy.shの1行目のPROJECT_IDを自身のプロジェクトに変更
3. `sh deploy.sh`
