import re
import requests
from slack_sdk.errors import SlackApiError
from core.slack import app
from core.env import SLACK_BOT_TOKEN
from utils.article import get_article_content
from utils.chat_gpt import summarize_and_recommend_with_gpt3, extract_keywords_with_gpt3
from core.gcp import extract_text_from_image


class SlackEvent:
    def __init__(self) -> None:
        self.client = app.client
        self.regist_handler()

    def regist_handler(self):
        app.event("message")(self.handle_message)

    # メッセージイベントをリッスンします
    def handle_message(self, event):
        # メッセージが自身から送信されたものであるかを確認
        auth_test_response = self.client.auth_test()
        bot_id = auth_test_response["user_id"]
        if event.get("user") == bot_id:
            return  # 自身からのメッセージは無視する

        # URLの正規表現パターン
        URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

        # メッセージのタイプを取得
        message_type = event.get("subtype", "")

        # スレッドのタイムスタンプを取得
        thread_ts = event.get('thread_ts', event['ts'])
        try:
            # メッセージがfile_shareイベントであるかを確認
            if message_type == "file_share":
                # 自身がメンションされていない場合は処理をスキップ
                if f"<@{bot_id}>" not in event["text"]:
                    return

                # ファイルの情報を取得
                file_info = event["files"][0]

                # ファイルが画像であるかを確認
                if file_info["mimetype"].startswith("image/"):

                    # 画像のURLを取得
                    url = file_info['url_private_download']

                    # Slackの認証トークンをヘッダーに設定
                    headers = {"Authorization": "Bearer %s" % SLACK_BOT_TOKEN}

                    # 画像をダウンロード
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        content = response.content
                    else:
                        print(f"Failed to download image: {response.status_code}")

                    texts = extract_text_from_image(content)

                    # テキストからキーワードを抽出
                    keywords = extract_keywords_with_gpt3(texts)

                    # 要約をユーザーに送信
                    self.client.chat_postMessage(channel=event['channel'], text=f"{keywords}", thread_ts=thread_ts)
            else:
                text = event["text"]

                # 自身がメンションされていない場合は処理をスキップ
                if f"<@{bot_id}>" not in text:
                    return

                # テキストからURLを抽出
                urls = re.findall(URL_PATTERN, text)
                if len(urls) == 0:
                    return

                # 最初のURLを使用して要約を実行
                url = urls[0]
                article_content = get_article_content(url)
                summary = summarize_and_recommend_with_gpt3(article_content)

                # 要約をユーザーに送信
                self.client.chat_postMessage(channel=event['channel'], text=summary, thread_ts=thread_ts, reply_broadcast=True)

        except SlackApiError as e:
            print(f"Error sending message: {e}")
