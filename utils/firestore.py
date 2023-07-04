from slack_sdk.oauth.installation_store import InstallationStore, Installation


class FirestoreInstallation(Installation):
    def __init__(
        self,
        bot_user_id=None,
        user_id=None,
        bot_token=None,
        enterprise_id=None,
        team_id=None,
        is_enterprise_install=False,
    ):
        super().__init__(
            bot_user_id=bot_user_id,
            user_id=user_id,
            enterprise_id=enterprise_id,
            team_id=team_id,
            is_enterprise_install=is_enterprise_install,
        )
        self.bot_token = bot_token


class FirestoreInstallationStore(InstallationStore):
    def __init__(self, db):
        self.db = db

    def save(self, installation):
        self.db.collection("installations").document(
            installation.to_bot().bot_token
        ).set(installation.to_dict())

    def find_installation(
        self,
        *,
        enterprise_id=None,
        team_id=None,
        user_id=None,
        is_enterprise_install=None
    ):
        query = (
            self.db.collection("installations")
            .where("enterprise_id", "==", enterprise_id)
            .where("team_id", "==", team_id)
            .limit(1)
        )
        docs = query.stream()
        for doc in docs:
            i = FirestoreInstallation()
            i.__dict__ = doc.to_dict()
            if i.enterprise_id == enterprise_id and i.team_id == team_id:
                return i
        return None


class FirestoreEvent:
    def __init__(
        self,
        workspace_id=None,
        channel_id=None,
        user_id=None,
        timestamp=None,
        image_url=None,
        image_text=None,
        keyword_text=None,
        article_url=None,
        article_text=None,
        summary_text=None,
    ):
        self.workspace_id = workspace_id
        self.channel_id = channel_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.image_url = image_url
        self.image_text = image_text
        self.keyword_text = keyword_text
        self.article_url = article_url
        self.article_text = article_text
        self.summary_text = summary_text

    def to_dict(self):
        return self.__dict__


class FirestoreEventStore:
    def __init__(self, db):
        self.db = db

    def save(self, event: FirestoreEvent):
        self.db.collection("slack_events").document().set(event.to_dict())
