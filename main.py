from core.slack import app, IgnoreRetryMiddleware
from core.gcp import db
from core.env import PORT
from utils.slack import SlackEvent

# Socket Modeを使用してアプリを起動します
if __name__ == "__main__":
    slack_event = SlackEvent(db=db)
    slack_event.regist_handler()
    app.use(IgnoreRetryMiddleware())
    app.use(slack_event.add_team_id_to_context)
    app.start(port=int(PORT))
