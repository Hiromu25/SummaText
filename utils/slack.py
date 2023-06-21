from io import BytesIO
import re
import requests
from PIL import Image
import pytesseract
from core.slack import app
from core.env import SLACK_BOT_TOKEN
from utils.article import get_article_content
from utils.chat_gpt import summarize_and_recommend_with_gpt3, extract_keywords_with_gpt3


class SlackEvent:
    def __init__(self) -> None:
        pass

    def regist_handler(self):
        self.handle_message

    # メッセージイベントをリッスンします
    @app.event("message")
    def handle_message(event, say):
        # URLの正規表現パターン
        URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

        # メッセージのタイプを取得
        message_type = event.get("subtype", "")

        # メッセージがfile_shareイベントであるかを確認
        if message_type == "file_share":
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
                    img = Image.open(BytesIO(response.content))
                else:
                    print(f"Failed to download image: {response.status_code}")

                # 画像から文字列を抽出
                text = pytesseract.image_to_string(img, lang="jpn+eng")

                # テキストからキーワードを抽出
                keywords = extract_keywords_with_gpt3(text)

                # 要約をユーザーに送信
                say(f"{keywords}")
        else:
            # メッセージのテキストを取得
            text = event["text"]

            # テキストからURLを抽出
            urls = re.findall(URL_PATTERN, text)
            if len(urls) == 0:
                return

            # 最初のURLを使用して要約を実行
            url = urls[0]
            article_content = get_article_content(url)
            summary = summarize_and_recommend_with_gpt3(article_content)

            # 要約をユーザーに送信
            say(f"{summary}\n{url}")
