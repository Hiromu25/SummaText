from core.env import SLACK_BOT_TOKEN, SLACK_SIGNING_SECRET
from slack_bolt import App

# Slack Bolt Appの初期化
app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
