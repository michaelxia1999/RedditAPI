from app.models import Model
from datetime import datetime
from pydantic import Field

class SubredditCreate(Model):
    name: str = Field(max_length=25)


class SubredditRead(Model):
    id: int
    name: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    follower_count: int
    user_display_name: str


class SubredditReads(Model):
    subreddits: list[SubredditRead]
    score_cursor: float
    id_cursor: int


class SubredditUpdate(Model):
    name: str | None = None
