from core.env import SLACK_CLIENT_SECRET, SLACK_CLIENT_ID, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.state_store import FileOAuthStateStore
from core.gcp import db
from utils.firestore import FirestoreInstallationStore

oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=[
        "chat:write",
        "im:history",
        "im:read",
        "im:write",
        "files:read",
        "channels:history",
        "channels:join",
    ],
    installation_store=FirestoreInstallationStore(db),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states"),
)

app = App(signing_secret=SLACK_SIGNING_SECRET, oauth_settings=oauth_settings)
