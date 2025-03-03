from app.db.schema import Comment, Post, PostUpvote, User
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased


async def create_post(
    title: str, body: list[dict], user_id: int, subreddit_id: int, db: AsyncSession
) -> int:
    query = (
        insert(Post)
        .values(title=title, body=body, user_id=user_id, subreddit_id=subreddit_id)
        .returning(Post.id)
    )
    result = await db.execute(query)
    post_id = result.scalars().one()
    return post_id


async def delete_post(post_id: int, user_id: int, db: AsyncSession) -> bool:
    query = delete(Post).where(Post.id == post_id, Post.user_id == user_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def update_post(post_id: int, user_id: int, post_data: dict, db: AsyncSession) -> bool:
    query = update(Post).where(Post.id == post_id, Post.user_id == user_id).values(**post_data)
    result = await db.execute(query)
    return result.rowcount > 0


# (Post, user_display_name, upvote_count, downvote_count, comment_count) | None
async def get_post(post_id: int, db: AsyncSession):
    Upvote = aliased(PostUpvote)
    Downvote = aliased(PostUpvote)

    query = (
        select(
            Post,
            User.display_name.label("user_display_name"),
            func.count(func.distinct(Upvote.id)).label("upvote_count"),  # Upvotes count
            func.count(func.distinct(Downvote.id)).label("downvote_count"),  # Downvotes count
            func.count(func.distinct(Comment.id)).label("comment_count"),  # Comments count
        )
        .join(User, Post.user_id == User.id, isouter=True)
        .join(Upvote, (Post.id == Upvote.post_id) & Upvote.value, isouter=True)
        .join(Downvote, (Post.id == Downvote.post_id) & ~Downvote.value, isouter=True)
        .join(Comment, Post.id == Comment.post_id, isouter=True)
        .where(Post.id == post_id)
        .group_by(Post.id, User.display_name)
    )
    result = await db.execute(query)
    row = result.first()
    return row


# ([(Post, user_display_name, upvote_count, downvote_count, comment_count, score_cursor)], next_score_cursor, next_id_cursor) | None
async def get_posts(
    search_query: str, db: AsyncSession, score_cursor: float | None, id_cursor: int | None
):
    Upvote = aliased(PostUpvote)
    Downvote = aliased(PostUpvote)

    limit = 3

    if score_cursor is None or id_cursor is None:
        query = (
            select(
                Post,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Comment.id)).label("comment_count"),
                func.similarity(Post.title, search_query).label("score_cursor"),
            )
            .join(User, Post.user_id == User.id, isouter=True)
            .join(Upvote, (Post.id == Upvote.post_id) & Upvote.value, isouter=True)
            .join(Downvote, (Post.id == Downvote.post_id) & ~Downvote.value, isouter=True)
            .join(Comment, Post.id == Comment.post_id, isouter=True)
            .group_by(Post.id, User.display_name)
            .order_by(
                func.similarity(Post.title, search_query).label("score_cursor").desc(),
                Post.id.asc(),
            )
            .limit(limit)
        )

    else:
        query = (
            select(
                Post,
                User.display_name.label("user_display_name"),
                func.count(func.distinct(Upvote.id)).label("upvote_count"),
                func.count(func.distinct(Downvote.id)).label("downvote_count"),
                func.count(func.distinct(Comment.id)).label("comment_count"),
                func.similarity(Post.title, search_query).label("score_cursor"),
            )
            .join(User, Post.user_id == User.id, isouter=True)
            .join(Upvote, (Post.id == Upvote.post_id) & Upvote.value, isouter=True)
            .join(Downvote, (Post.id == Downvote.post_id) & ~Downvote.value, isouter=True)
            .join(Comment, Post.id == Comment.post_id, isouter=True)
            .where(
                (func.similarity(Post.title, search_query) < score_cursor)
                | (
                    (func.similarity(Post.title, search_query) == score_cursor)
                    & (Post.id > id_cursor)
                )
            )
            .group_by(Post.id, User.display_name)
            .order_by(
                func.similarity(Post.title, search_query).label("score_cursor").desc(),
                Post.id.asc(),
            )
            .limit(limit)
        )

    result = await db.execute(query)
    rows = result.all()

    if rows == []:
        return None

    next_score_cursor = rows[-1][-1]
    next_id_cursor = rows[-1][0].id

    return (rows, next_score_cursor, next_id_cursor)


async def upvote_post(value: bool, user_id: int, post_id: int, db: AsyncSession) -> bool:
    query = insert(PostUpvote).values(value=value, user_id=user_id, post_id=post_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def delete_post_upvote(user_id: int, post_id: int, db: AsyncSession) -> bool:
    query = delete(PostUpvote).where(PostUpvote.user_id == user_id, PostUpvote.post_id == post_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def toggle_post_upvote(user_id: int, post_id: int, db: AsyncSession) -> bool:
    query = (
        update(PostUpvote)
        .where(PostUpvote.user_id == user_id, PostUpvote.post_id == post_id)
        .values(value=~PostUpvote.value)
    )
    result = await db.execute(query)
    return result.rowcount > 0
