import re
from core.slack import app
from utils.article import get_article_content
from utils.chat_gpt import summarize_and_recommend_with_gpt3

class SlackEvent:
    def __init__(self) -> None:
        pass

    def regist_handler(self):
        self.handle_message

    # メッセージイベントをリッスンします
    @app.message()
    def handle_message(message, say):
        # URLの正規表現パターン
        URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        # メッセージのテキストを取得
        text = message['text']

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
