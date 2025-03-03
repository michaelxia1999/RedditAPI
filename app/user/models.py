from app.models import Model
from datetime import datetime
from pydantic import Field


class UserCreate(Model):
    username: str = Field(max_length=25)
    password: str = Field(max_length=25)
    email: str
    display_name: str
    avatar: str


class UserUpdate(Model):
    password: str | None = Field(None, max_length=25)
    email: str | None = Field(None, max_length=25)
    display_name: str | None = None
    avatar: str | None = None


class UserRead(Model):
    id: int
    username: str
    password: str
    email: str
    display_name: str
    avatar: str
    created_at: datetime
    updated_at: datetime
