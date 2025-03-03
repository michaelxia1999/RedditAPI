from app.models import Markdown, Model
from datetime import datetime


class PostCreate(Model):
    title: str
    body: list[Markdown]


class PostRead(Model):
    id: int
    title: str
    user_id: int
    body: list[Markdown]
    subreddit_id: int
    created_at: datetime
    updated_at: datetime
    user_display_name: str
    upvote_count: int
    downvote_count: int
    comment_count: int


class PostReads(Model):
    posts: list[PostRead]
    score_cursor: float
    id_cursor: int


class PostUpdate(Model):
    title: str | None = None
    body: list[Markdown] | None = None


class PostUpvoteCreate(Model):
    value: bool
