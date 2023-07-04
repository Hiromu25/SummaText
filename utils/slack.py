import re
import requests
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from slack_bolt import BoltContext
from core.slack import app, FirestoreInstallationStore
from utils.article import get_article_content
from utils.chat_gpt import summarize_and_recommend_with_gpt3, extract_keywords_with_gpt3
from utils.firestore import FirestoreEvent, FirestoreEventStore
from core.gcp import extract_text_from_image


def download_image(file_info, installation):
    if file_info["mimetype"].startswith("image/"):
        url = file_info["url_private_download"]
        headers = {"Authorization": "Bearer %s" % installation.bot_token}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.content
            return content, url
        else:
            print(f"Failed to download image: {response.status_code}")
            raise Exception("Failed to download image")
    else:
        raise Exception("File is not an image")


class SlackEvent:
    def __init__(self, db) -> None:
        self.db = db
        self.regist_handler()

    def regist_handler(self):
        app.event("message")(self.handle_message)

    def handle_message(self, event, context: BoltContext):
        try:
            team_id = context["team_id"]
            if team_id is None:
                print("The event does not contain a 'team' or 'user_team' key.")
                return
            installation = FirestoreInstallationStore(self.db).find_installation(
                team_id=team_id
            )

            bot_id = installation.bot_user_id
            user_id = event.get("user")
            # ボット自身のメッセージの場合は何もしない
            if user_id == bot_id:
                return

            client = WebClient(token=installation.bot_token)
            message_type = event.get("subtype", "")
            thread_ts = event.get("thread_ts", event["ts"])

            # Check if bot is mentioned in the message
            is_bot_mentioned = False
            if "blocks" in event:
                for block in event["blocks"]:
                    if block["type"] == "rich_text":
                        for element in block["elements"]:
                            if element["type"] == "rich_text_section":
                                for item in element["elements"]:
                                    if item["type"] == "user" and item["user_id"] == bot_id:
                                        is_bot_mentioned = True
                                        break

            if message_type == "file_share" and is_bot_mentioned:

                # Slackから画像をダウンロード
                file_info = event["files"][0]
                content, url = download_image(file_info, installation)

                # OCRを用いて画像から文字列を抽出
                texts = extract_text_from_image(content)

                # chatGPTを用いて抽出された文字列からキーワードを抽出
                keywords = extract_keywords_with_gpt3(texts)

                # slackにメッセージを送信
                client.chat_postMessage(
                    channel=event["channel"],
                    text=f"{keywords}",
                    thread_ts=thread_ts,
                )

                # Save to Firestore
                event_store = FirestoreEventStore(self.db)
                event = FirestoreEvent(
                    workspace_id=team_id,
                    channel_id=event["channel"],
                    user_id=user_id,
                    timestamp=event["ts"],
                    image_url=url,
                    image_text=texts,
                    keyword_text=keywords,
                )
                event_store.save(event)

            elif is_bot_mentioned:

                if "text" in event:
                    text = event["text"]
                else:
                    text = ""
                # slackメッセージからURL文字列を抽出
                URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
                urls = re.findall(URL_PATTERN, text)
                if len(urls) == 0:
                    return

                url = urls[0]
                # URLから文章を抽出
                article_content = get_article_content(url)

                # chatGPTを用いて文章を要約した文章を取得
                summary = summarize_and_recommend_with_gpt3(article_content)

                # slackにメッセージを送信
                client.chat_postMessage(
                    channel=event["channel"],
                    text=summary,
                    thread_ts=thread_ts,
                    reply_broadcast=True,
                )

                # Save to Firestore
                event_store = FirestoreEventStore(self.db)
                event = FirestoreEvent(
                    workspace_id=team_id,
                    channel_id=event["channel"],
                    user_id=user_id,
                    timestamp=event["ts"],
                    article_url=url,
                    article_text=article_content,
                    summary_text=summary,
                )
                event_store.save(event)

        except SlackApiError as e:
            print(f"Error sending message: {e}")
        except Exception as e:
            print(f"Error: {e}")
