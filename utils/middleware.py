from typing import Awaitable, Callable
from slack_bolt.middleware.middleware import Middleware
from slack_bolt.request import BoltRequest
from slack_bolt.response import BoltResponse


class IgnoreRetryMiddleware(Middleware):
    def process(
        self, req: BoltRequest, resp: BoltResponse, next: Callable[..., Awaitable[None]]
    ):
        if "x-slack-retry-num" in req.headers:
            # If the 'x-slack-retry-num' header is present, ignore the request
            return
        else:
            # Otherwise, continue processing the request
            next()


class TeamIdContextMiddleware(Middleware):
    def process(
        self, req: BoltRequest, resp: BoltResponse, next: Callable[..., Awaitable[None]]
    ):
        team_id = req.body.get("team_id", req.body["event"].get("team"))
        req.context["team_id"] = team_id
        next()
