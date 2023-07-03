import re
import requests
from slack_sdk.errors import SlackApiError
from slack_sdk import WebClient
from slack_bolt import BoltContext
from core.slack import app, FirestoreInstallationStore
from utils.article import get_article_content
from utils.chat_gpt import summarize_and_recommend_with_gpt3, extract_keywords_with_gpt3
from core.gcp import extract_text_from_image

class SlackEvent:
    def __init__(self, db) -> None:
        self.db = db
        self.regist_handler()

    def regist_handler(self):
        app.event("message")(self.handle_message)

    def add_team_id_to_context(self, client, req, resp, next):
        team_id = req.body.get('team_id', req.body['event'].get('team'))
        req.context['team_id'] = team_id
        next()

    def handle_message(self, event, context: BoltContext):
        print(event)
        team_id = context['team_id']
        if team_id is None:
            print("The event does not contain a 'team' or 'user_team' key.")
            return
        installation = FirestoreInstallationStore(self.db).find_installation(team_id=team_id)
        client = WebClient(token=installation.bot_token)
        bot_id = installation.bot_user_id
        user_id = event.get('user')
        if user_id == bot_id:
            return

        URL_PATTERN = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"
        message_type = event.get("subtype", "")
        thread_ts = event.get('thread_ts', event['ts'])
        try:
            if message_type == "file_share":
                if f"<@{bot_id}>" not in event["text"]:
                    return

                file_info = event["files"][0]
                if file_info["mimetype"].startswith("image/"):
                    url = file_info['url_private_download']
                    headers = {"Authorization": "Bearer %s" % installation.bot_token}
                    response = requests.get(url, headers=headers)
                    if response.status_code == 200:
                        content = response.content
                    else:
                        print(f"Failed to download image: {response.status_code}")

                    texts = extract_text_from_image(content)
                    keywords = extract_keywords_with_gpt3(texts)
                    client.chat_postMessage(channel=event['channel'], text=f"{keywords}", thread_ts=thread_ts)

                    # Save to Firestore
                    doc_ref = self.db.collection('slack_events').document()
                    doc_ref.set({
                        'workspace_id': team_id,
                        'channel_id': event['channel'],
                        'user_id': user_id,
                        'timestamp': event['ts'],
                        'image_url': url,
                        'image_text': texts,
                        'keyword_text': keywords
                    })

            else:
                if "text" in event:
                    text = event["text"]
                else:
                    text = ""

                if f"<@{bot_id}>" not in text:
                    return

                urls = re.findall(URL_PATTERN, text)
                if len(urls) == 0:
                    return

                url = urls[0]
                article_content = get_article_content(url)
                summary = summarize_and_recommend_with_gpt3(article_content)
                client.chat_postMessage(channel=event['channel'], text=summary, thread_ts=thread_ts, reply_broadcast=True)

                # Save to Firestore
                doc_ref = self.db.collection('slack_events').document()
                doc_ref.set({
                    'workspace_id': team_id,
                    'channel_id': event['channel'],
                    'user_id': user_id,
                    'timestamp': event['ts'],
                    'article_url': url,
                    'article_text': article_content,
                    'summary_text': summary
                })

        except SlackApiError as e:
            print(f"Error sending message: {e}")
