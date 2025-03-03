from app.models import Markdown, Model
from datetime import datetime


class CommentCreate(Model):
    parent_comment_id: int | None
    body: list[Markdown]


class CommentRead(Model):
    id: int
    user_id: int
    body: list[Markdown]
    post_id: int
    parent_comment_id: int | None
    created_at: datetime
    updated_at: datetime
    user_display_name: str
    upvote_count: int
    downvote_count: int
    reply_count: int


class CommentReads(Model):
    comments: list[CommentRead]
    score_cursor: int
    id_cursor: int


class CommentUpdate(Model):
    body: list[Markdown] | None = None


class CommentUpvoteCreate(Model):
    value: bool
