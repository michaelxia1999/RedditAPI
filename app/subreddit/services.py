from app.db.schema import Subreddit, SubredditFollow, User
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession


async def create_subreddit(subreddit_name: str, user_id: int, db: AsyncSession) -> int:
    query = insert(Subreddit).values(name=subreddit_name, user_id=user_id).returning(Subreddit.id)
    result = await db.execute(query)
    subreddit_id = result.scalars().one()
    return subreddit_id


async def delete_subreddit(subreddit_id: int, user_id: int, db: AsyncSession) -> bool:
    query = delete(Subreddit).where(Subreddit.id == subreddit_id, Subreddit.user_id == user_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def update_subreddit(
    subreddit_id: int, user_id: int, subreddit_data: dict, db: AsyncSession
) -> bool:
    query = (
        update(Subreddit)
        .where(Subreddit.id == subreddit_id, Subreddit.user_id == user_id)
        .values(**subreddit_data)
    )
    result = await db.execute(query)
    return result.rowcount > 0


# (Subreddit, user_display_name, follower_count) | None
async def get_subreddit(subreddit_id: int, db: AsyncSession):
    query = (
        select(
            Subreddit,
            User.display_name.label("user_display_name"),
            func.count(SubredditFollow.id).label("follower_count"),
        )
        .join(User, Subreddit.user_id == User.id, isouter=True)
        .join(SubredditFollow, Subreddit.id == SubredditFollow.subreddit_id, isouter=True)
        .where(Subreddit.id == subreddit_id)
        .group_by(Subreddit.id, User.display_name)
    )

    result = await db.execute(query)
    row = result.first()
    return row


# ([(Subreddit, user_display_name, follower_count, score_cursor)], next_score_cursor, next_id_cursor) | None
async def get_subreddits(
    search_query: str, db: AsyncSession, score_cursor: float | None, id_cursor: int | None
):
    limit = 10

    if score_cursor is None or id is None:
        query = (
            select(
                Subreddit,
                User.display_name.label("user_display_name"),
                func.count(SubredditFollow.id).label("follower_count"),
                func.similarity(Subreddit.name, search_query).label("score_cursor"),
            )
            .join(User, Subreddit.user_id == User.id, isouter=True)
            .join(SubredditFollow, Subreddit.id == SubredditFollow.subreddit_id, isouter=True)
            .group_by(Subreddit.id, User.display_name)
            .order_by(
                func.similarity(Subreddit.name, search_query).label("score_cursor").desc(),
                Subreddit.id.asc(),
            )
            .limit(limit)
        )

    else:
        query = (
            select(
                Subreddit,
                User.display_name.label("user_display_name"),
                func.count(SubredditFollow.id).label("follower_count"),
                func.similarity(Subreddit.name, search_query).label("score_cursor"),
            )
            .join(User, Subreddit.user_id == User.id, isouter=True)
            .join(SubredditFollow, Subreddit.id == SubredditFollow.subreddit_id, isouter=True)
            .where(
                (func.similarity(Subreddit.name, search_query) < score_cursor)
                | (
                    (func.similarity(Subreddit.name, search_query) == score_cursor)
                    & (Subreddit.id > id_cursor)
                )
            )
            .group_by(Subreddit.id, User.display_name)
            .order_by(
                func.similarity(Subreddit.name, search_query).label("score_cursor").desc(),
                Subreddit.id.asc(),
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


async def follow_subreddit(user_id: int, subreddit_id: int, db: AsyncSession) -> bool:
    query = insert(SubredditFollow).values(subreddit_id=subreddit_id, user_id=user_id)
    result = await db.execute(query)
    return result.rowcount > 0


async def unfollow_subreddit(user_id: int, subreddit_id: int, db: AsyncSession) -> bool:
    query = delete(SubredditFollow).where(
        SubredditFollow.subreddit_id == subreddit_id, SubredditFollow.user_id == user_id
    )
    result = await db.execute(query)
    return result.rowcount > 0


async def subreddit_name_exists(subreddit_name: str, db: AsyncSession) -> bool:
    query = select(Subreddit).where(Subreddit.name == subreddit_name)
    result = await db.execute(query)
    subreddit = result.scalars().first()

    return True if subreddit else False
