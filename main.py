import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv
import openai
from newspaper import Article

# OpenAIのAPIキーを設定します
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ウェブサイトから記事の内容を取得する関数
def get_article_content(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

# GPT-3.5を使用してテキストを要約し、それがどのような人におすすめかを述べる関数
def summarize_and_recommend_with_gpt3(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a talented writer with a knack for captivating summaries. Imagine you are crafting a compelling headline to entice readers to dive into the article. Summarize the content in three sentences, making it engaging and intriguing. After the summary, also provide a recommendation on who would find this article most beneficial. Write in Japanese."},
            {"role": "user", "content": f"Summarize this and recommend who would benefit: {text}"},
        ],
        max_tokens=1024,
    )
    return response.choices[0].message['content']

# URLの正規表現パターン
URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

# Slack Bolt Appの初期化
app = App(token=os.getenv("SLACK_BOT_TOKEN"), signing_secret=os.getenv("SLACK_SIGNING_SECRET"))

# メッセージイベントをリッスンします
@app.message()
def handle_message(message, say):
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

# Socket Modeを使用してアプリを起動します
if __name__ == "__main__":
    SocketModeHandler(app, os.getenv("SLACK_APP_TOKEN")).start()