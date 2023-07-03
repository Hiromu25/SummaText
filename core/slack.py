from typing import Awaitable, Callable
from core.env import SLACK_CLIENT_SECRET, SLACK_CLIENT_ID, SLACK_SIGNING_SECRET
from slack_bolt import App
from slack_sdk.oauth.installation_store import InstallationStore, Installation
from slack_bolt.oauth.oauth_settings import OAuthSettings
from slack_sdk.oauth.state_store import FileOAuthStateStore
from core.gcp import db

from slack_sdk.oauth.installation_store import InstallationStore, Bot, Installation

from slack_bolt import BoltContext
from slack_bolt.middleware.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse

class IgnoreRetryMiddleware(Middleware):
    def process(self, req: BoltRequest, resp: BoltResponse, next: Callable[..., Awaitable[None]]):
        if 'x-slack-retry-num' in req.headers:
            # If the 'x-slack-retry-num' header is present, ignore the request
            return
        else:
            # Otherwise, continue processing the request
            next()

class FirestoreInstallation(Installation):
    def __init__(self,bot_user_id=None, user_id=None, bot_token=None, enterprise_id=None, team_id=None, is_enterprise_install=False):
        super().__init__(bot_user_id=bot_user_id, user_id=user_id, enterprise_id=enterprise_id, team_id=team_id, is_enterprise_install=is_enterprise_install)
        self.bot_token = bot_token

class FirestoreInstallationStore(InstallationStore):
    def __init__(self, db):
        self.db = db

    def save(self, installation):
        self.db.collection('installations').document(installation.to_bot().bot_token).set(installation.to_dict())

    def find_installation(self, *, enterprise_id=None, team_id=None, user_id=None, is_enterprise_install=None):
        query = self.db.collection('installations').where('enterprise_id', '==', enterprise_id).where('team_id', '==', team_id).limit(1)
        docs = query.stream()
        for doc in docs:
            i = FirestoreInstallation()
            i.__dict__ = doc.to_dict()
            if i.enterprise_id == enterprise_id and i.team_id == team_id:
                return i
        return None


oauth_settings = OAuthSettings(
    client_id=SLACK_CLIENT_ID,
    client_secret=SLACK_CLIENT_SECRET,
    scopes=["chat:write", "im:history", "im:read", "im:write", "files:read", "channels:history", "channels:join"],
    installation_store=FirestoreInstallationStore(db),
    state_store=FileOAuthStateStore(expiration_seconds=600, base_dir="./data/states")
)

app = App(
    signing_secret=SLACK_SIGNING_SECRET,
    oauth_settings=oauth_settings,
)
