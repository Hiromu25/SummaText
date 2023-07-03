from slack_bolt.adapter.socket_mode import SocketModeHandler
from core.slack import app, IgnoreRetryMiddleware
from core.env import SLACK_APP_TOKEN
from utils.slack import SlackEvent
import os

# Socket Modeを使用してアプリを起動します
if __name__ == "__main__":
    slack_event = SlackEvent()
    slack_event.regist_handler()
    # SocketModeHandler(app, SLACK_APP_TOKEN).start()
    app.use(IgnoreRetryMiddleware())
    app.start(port=int(os.environ.get("PORT", 8080)))
