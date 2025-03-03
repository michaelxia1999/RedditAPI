from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(pg.INTEGER, primary_key=True, sort_order=-1)
    created_at: Mapped[datetime] = mapped_column(pg.TIMESTAMP(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        pg.TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now()
    )

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_sa_")}


class User(Base):
    __tablename__ = "user"
    username: Mapped[str] = mapped_column(pg.VARCHAR(25), unique=True)
    password: Mapped[str] = mapped_column(pg.VARCHAR(256))
    email: Mapped[str] = mapped_column(pg.TEXT, unique=True)
    display_name: Mapped[str] = mapped_column(pg.VARCHAR(25), unique=True)
    avatar: Mapped[str] = mapped_column(pg.TEXT)


class Subreddit(Base):
    __tablename__ = "subreddit"
    name: Mapped[str] = mapped_column(pg.VARCHAR(25), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="RESTRICT"))


class SubredditFollow(Base):
    __tablename__ = "subreddit_follow"
    subreddit_id: Mapped[int] = mapped_column(ForeignKey(column=Subreddit.id, ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="CASCADE"))

    UniqueConstraint(subreddit_id, user_id)


class Post(Base):
    __tablename__ = "post"
    title: Mapped[str] = mapped_column(pg.TEXT)
    body: Mapped[list[dict]] = mapped_column(pg.JSONB)
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="CASCADE"))
    subreddit_id: Mapped[int] = mapped_column(ForeignKey(column=Subreddit.id, ondelete="CASCADE"))


class Comment(Base):
    __tablename__ = "comment"
    body: Mapped[list[dict]] = mapped_column(pg.JSONB)
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey(column=Post.id, ondelete="CASCADE"))
    parent_comment_id: Mapped[int | None] = mapped_column(
        ForeignKey(column="comment.id", ondelete="CASCADE"), nullable=True
    )  # None = post_comment


class PostUpvote(Base):
    __tablename__ = "post_upvote"
    value: Mapped[bool] = mapped_column(pg.BOOLEAN)
    post_id: Mapped[int] = mapped_column(ForeignKey(column=Post.id, ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="CASCADE"))
    UniqueConstraint(post_id, user_id)


class CommentUpvote(Base):
    __tablename__ = "comment_upvote"
    value: Mapped[bool] = mapped_column(pg.BOOLEAN)
    comment_id: Mapped[int] = mapped_column(ForeignKey(column=Comment.id, ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey(column=User.id, ondelete="CASCADE"))
    UniqueConstraint(comment_id, user_id)
