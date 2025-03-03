from app.auth.services import get_current_user_id
from app.db.core import get_db
from app.subreddit.exceptions import SubredditNameAlreadyExist, SubredditNotFound
from app.subreddit.models import SubredditCreate, SubredditRead, SubredditReads, SubredditUpdate
from app.subreddit.services import (
    create_subreddit,
    delete_subreddit,
    follow_subreddit,
    get_subreddit,
    get_subreddits,
    subreddit_name_exists,
    unfollow_subreddit,
    update_subreddit,
)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

subreddit_router = APIRouter(prefix="/subreddits", tags=["Subreddit"])


@subreddit_router.post(path="", status_code=201, response_model=SubredditRead)
async def create_subreddit_route(
    subreddit_data: SubredditCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if await subreddit_name_exists(subreddit_name=subreddit_data.name, db=db):
        raise SubredditNameAlreadyExist()

    subreddit_id = await create_subreddit(
        subreddit_name=subreddit_data.name, user_id=current_user_id, db=db
    )

    subreddit = await get_subreddit(subreddit_id=subreddit_id, db=db)
    if subreddit is None:
        raise SubredditNotFound()

    subreddit = subreddit._asdict()
    subreddit.update(subreddit.pop("Subreddit").to_dict())
    return subreddit


@subreddit_router.get(path="", status_code=200, response_model=SubredditReads)
async def get_subreddits_route(
    search_query: str,
    score_cursor: float | None = None,
    id_cursor: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await get_subreddits(
        search_query=search_query, db=db, score_cursor=score_cursor, id_cursor=id_cursor
    )
    if result is None:
        raise SubredditNotFound()

    subreddits, next_score_cursor, next_id_cursor = result

    res = {"subreddits": [], "score_cursor": next_score_cursor, "id_cursor": next_id_cursor}

    for subreddit in subreddits:
        subreddit = subreddit._asdict()
        subreddit.pop("score_cursor")
        subreddit.update(subreddit.pop("Subreddit").to_dict())
        res["subreddits"].append(subreddit)

    return res


@subreddit_router.get(path="/{subreddit_id}", status_code=200, response_model=SubredditRead)
async def get_subreddit_route(subreddit_id: int, db: AsyncSession = Depends(get_db)):
    subreddit = await get_subreddit(subreddit_id=subreddit_id, db=db)

    if not subreddit:
        raise SubredditNotFound()

    subreddit = subreddit._asdict()
    subreddit.update(subreddit.pop("Subreddit").to_dict())
    return subreddit


@subreddit_router.patch(path="/{subreddit_id}", status_code=201, response_model=SubredditRead)
async def update_subreddit_route(
    subreddit_id: int,
    subreddit_data: SubredditUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if subreddit_data.name and await subreddit_name_exists(
        subreddit_name=subreddit_data.name, db=db
    ):
        raise SubredditNameAlreadyExist()

    if not await update_subreddit(
        subreddit_id=subreddit_id,
        user_id=current_user_id,
        subreddit_data=subreddit_data.model_dump(exclude_unset=True),
        db=db,
    ):
        raise SubredditNotFound()

    subreddit = await get_subreddit(subreddit_id=subreddit_id, db=db)

    if not subreddit:
        raise SubredditNotFound()

    subreddit = subreddit._asdict()
    subreddit.update(subreddit.pop("Subreddit").to_dict())
    return subreddit


@subreddit_router.delete(path="/{subreddit_id}", response_model=None)
async def delete_subreddit_route(
    subreddit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await delete_subreddit(subreddit_id=subreddit_id, user_id=current_user_id, db=db):
        raise SubredditNotFound()


@subreddit_router.post(path="/{subreddit_id}/followers", response_model=None)
async def follow_subreddit_route(
    subreddit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await follow_subreddit(user_id=current_user_id, subreddit_id=subreddit_id, db=db):
        raise SubredditNotFound()


@subreddit_router.delete(path="/{subreddit_id}/followers", response_model=None)
async def unfollow_subreddit_route(
    subreddit_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await unfollow_subreddit(user_id=current_user_id, subreddit_id=subreddit_id, db=db):
        raise SubredditNotFound()
