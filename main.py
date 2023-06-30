from slack_bolt.adapter.socket_mode import SocketModeHandler
from core.slack import app
from core.env import SLACK_APP_TOKEN, PORT
from utils.slack import SlackEvent

# Socket Modeを使用してアプリを起動します
if __name__ == "__main__":
    slack_event = SlackEvent()
    slack_event.regist_handler()
    # SocketModeHandler(app, SLACK_APP_TOKEN).start()
    app.start(port=PORT)
