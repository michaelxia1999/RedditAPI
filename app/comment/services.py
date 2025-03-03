from app.db.schema import Comment, CommentUpvote, User
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased


async def submit_comment(
    body: list[dict], user_id: int, post_id: int, parent_comment_id: int | None, db: AsyncSession
) -> int:
    query = (
        insert(Comment)
        .values(body=body, user_id=user_id, post_id=post_id, parent_comment_id=parent_comment_id)
        .returning(Comment.id)
    )
    result = await db.execute(query)
    comment_id = result.scalars().one()
    return comment_id


async def delete_comment(comment_id: int, user_id: int, db: AsyncSession):
    query = delete(Comment).where(Comment.id == comment_id, Comment.user_id == user_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def update_comment(
    comment_id: int, user_id: int, comment_data: dict, db: AsyncSession
) -> bool:
    query = (
        update(Comment)
        .where(Comment.id == comment_id, Comment.user_id == user_id)
        .values(**comment_data)
    )
    result = await db.execute(query)
    return result.rowcount > 0


async def upvote_comment(user_id: int, comment_id: int, value: bool, db: AsyncSession) -> bool:
    query = insert(CommentUpvote).values(value=value, user_id=user_id, comment_id=comment_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def toggle_comment_upvote(user_id: int, comment_id: int, db: AsyncSession) -> bool:
    query = (
        update(CommentUpvote)
        .where(CommentUpvote.user_id == user_id, CommentUpvote.comment_id == comment_id)
        .values(value=~CommentUpvote.value)
    )
    result = await db.execute(query)
    return result.rowcount > 0


async def delete_comment_upvote(user_id: int, comment_id: int, db: AsyncSession) -> bool:
    query = delete(CommentUpvote).where(
        CommentUpvote.user_id == user_id, CommentUpvote.comment_id == comment_id
    )
    result = await db.execute(query)
    return result.rowcount > 0


# (Comment, user_display_name, upvote_count, downvote_count, reply_count) | None
async def get_comment(comment_id: int, db: AsyncSession):
    Upvote = aliased(CommentUpvote)
    Downvote = aliased(CommentUpvote)
    CommentReply = aliased(Comment)

    query = (
        select(
            Comment,
            User.display_name.label("user_display_name"),
            func.count(func.distinct(Upvote.id)).label("upvote_count"),
            func.count(func.distinct(Downvote.id)).label("downvote_count"),
            func.count(func.distinct(CommentReply.id)).label("reply_count"),
        )
        .join(User, Comment.user_id == User.id, isouter=True)
        .join(Upvote, (Comment.id == Upvote.comment_id) & Upvote.value, isouter=True)
        .join(Downvote, (Comment.id == Downvote.comment_id) & ~Downvote.value, isouter=True)
        .join(CommentReply, CommentReply.parent_comment_id == Comment.id, isouter=True)
        .where(Comment.id == comment_id)
        .group_by(Comment.id, User.display_name)
    )
    result = await db.execute(query)
    row = result.first()
    return row


# [(Comment, user_display_name, upvote_count, downvote_count, reply_count), next_score_cursor, next_id_cursor] | None
async def get_comments(
    post_id: int, db: AsyncSession, score_cursor: int | None, id_cursor: int | None
):
    limit = 1

    Upvote = aliased(CommentUpvote)
    Downvote = aliased(CommentUpvote)
    Reply = aliased(Comment)

    if score_cursor is None or id_cursor is None:
        query = (
            select(
                Comment,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Reply.id)).label("reply_count"),
            )
            .join(User, Comment.user_id == User.id, isouter=True)
            .join(Upvote, (Comment.id == Upvote.comment_id) & Upvote.value, isouter=True)
            .join(Downvote, (Comment.id == Downvote.comment_id) & ~Downvote.value, isouter=True)
            .join(Reply, Reply.parent_comment_id == Comment.id, isouter=True)
            .where(Comment.post_id == post_id)
            .group_by(Comment.id, User.display_name)
            .order_by(
                func.count(func.distinct(Upvote.id)).label("upvote_count").desc(), Comment.id.asc()
            )
            .limit(limit)
        )
    else:
        query = (
            select(
                Comment,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Reply.id)).label("reply_count"),
            )
            .join(User, Comment.user_id == User.id, isouter=True)
            .join(Upvote, (Comment.id == Upvote.comment_id) & Upvote.value, isouter=True)
            .join(Downvote, (Comment.id == Downvote.comment_id) & ~Downvote.value, isouter=True)
            .join(Reply, Reply.parent_comment_id == Comment.id, isouter=True)
            .where(Comment.post_id == post_id)
            .group_by(Comment.id, User.display_name)
            .having(
                (func.count(func.distinct(Upvote.id)) < score_cursor)
                | (
                    (func.count(func.distinct(Upvote.id)) == score_cursor)
                    & (Comment.id > id_cursor)
                )
            )
            .order_by(func.count(func.distinct(Upvote.id)).desc(), Comment.id.asc())
            .limit(limit)
        )

    result = await db.execute(query)
    rows = result.all()

    if rows == []:
        return None

    next_score_cursor = rows[-1][2]
    next_id_cursor = rows[-1][0].id

    return (rows, next_score_cursor, next_id_cursor)


# [(Comment, user_display_name, upvote_count, downvote_count, reply_count), next_score_cursor, next_id_cursor] | None
async def get_comment_replies(
    comment_id: int, db: AsyncSession, score_cursor: int | None, id_cursor: int | None
):
    limit = 10

    Upvote = aliased(CommentUpvote)
    Downvote = aliased(CommentUpvote)
    Reply = aliased(Comment)

    if score_cursor is None or id_cursor is None:
        query = (
            select(
                Comment,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Reply.id)).label("reply_count"),
            )
            .join(User, Comment.user_id == User.id, isouter=True)
            .join(Upvote, (Comment.id == Upvote.comment_id) & Upvote.value, isouter=True)
            .join(Downvote, (Comment.id == Downvote.comment_id) & ~Downvote.value, isouter=True)
            .join(Reply, Reply.parent_comment_id == Comment.id, isouter=True)
            .where(Comment.parent_comment_id == comment_id)
            .group_by(Comment.id, User.display_name)
            .order_by(
                func.count(func.distinct(Upvote.id)).label("upvote_count").desc(), Comment.id.asc()
            )
            .limit(limit)
        )
    else:
        query = (
            select(
                Comment,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Reply.id)).label("reply_count"),
            )
            .join(User, Comment.user_id == User.id, isouter=True)
            .join(Upvote, (Comment.id == Upvote.comment_id) & Upvote.value, isouter=True)
            .join(Downvote, (Comment.id == Downvote.comment_id) & ~Downvote.value, isouter=True)
            .join(Reply, Reply.parent_comment_id == Comment.id, isouter=True)
            .where(Comment.parent_comment_id == comment_id)
            .group_by(Comment.id, User.display_name)
            .having(
                (func.count(func.distinct(Upvote.id)) < score_cursor)
                | (
                    (func.count(func.distinct(Upvote.id)) == score_cursor)
                    & (Comment.id > id_cursor)
                )
            )
            .order_by(func.count(func.distinct(Upvote.id)).desc(), Comment.id.asc())
            .limit(limit)
        )

    result = await db.execute(query)
    rows = result.all()

    if rows == []:
        return None

    next_score_cursor = rows[-1][2]
    next_id_cursor = rows[-1][0].id

    return (rows, next_score_cursor, next_id_cursor)
