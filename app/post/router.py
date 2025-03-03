from app.auth.services import get_current_user_id
from app.db.core import get_db
from app.post.exceptions import PostNotFound, PostUpvoteNotFound
from app.post.models import PostCreate, PostRead, PostReads, PostUpdate, PostUpvoteCreate
from app.post.services import (
    create_post,
    delete_post,
    delete_post_upvote,
    get_post,
    get_posts,
    toggle_post_upvote,
    update_post,
    upvote_post,
)
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

post_router = APIRouter(prefix="/subreddits/{subreddit_id}/posts", tags=["Post"])


@post_router.post(path="", status_code=201, response_model=PostRead)
async def create_post_route(
    subreddit_id: int,
    post_data: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    post_id = await create_post(
        title=post_data.title,
        body=[elem.model_dump() for elem in post_data.body],
        user_id=current_user_id,
        subreddit_id=subreddit_id,
        db=db,
    )

    post = await get_post(post_id=post_id, db=db)

    if not post:
        raise PostNotFound()

    post = post._asdict()
    post.update(post.pop("Post").to_dict())
    return post


@post_router.get(path="", status_code=200, response_model=PostReads)
async def get_posts_route(
    search_query: str,
    score_cursor: float | None = None,
    id_cursor: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await get_posts(
        search_query=search_query, db=db, score_cursor=score_cursor, id_cursor=id_cursor
    )
    if result is None:
        raise PostNotFound()

    posts, next_score_cursor, next_id_cursor = result

    res = {"posts": [], "score_cursor": next_score_cursor, "id_cursor": next_id_cursor}

    for post in posts:
        post = post._asdict()
        print(post.pop("score_cursor"))
        post.update(post.pop("Post").to_dict())
        res["posts"].append(post)

    return res


@post_router.get(path="/{post_id}", status_code=200, response_model=PostRead)
async def get_post_route(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await get_post(post_id=post_id, db=db)

    if not post:
        raise PostNotFound()

    post = post._asdict()
    post.update(post.pop("Post").to_dict())
    return post


@post_router.delete(path="/{post_id}", status_code=200, response_model=None)
async def delete_post_route(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not delete_post(post_id=post_id, user_id=current_user_id, db=db):
        raise PostNotFound()


@post_router.patch(path="/{post_id}", status_code=200, response_model=PostRead)
async def update_post_route(
    post_id: int,
    post_data: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await update_post(
        post_id=post_id,
        user_id=current_user_id,
        post_data=post_data.model_dump(exclude_unset=True),
        db=db,
    ):
        raise PostNotFound()

    post = await get_post(post_id=post_id, db=db)

    if not post:
        raise PostNotFound()

    post = post._asdict()
    post.update(post.pop("Post").to_dict())
    return post


@post_router.post(path="/{post_id}/upvote", status_code=201, response_model=None)
async def upvote_post_route(
    post_id: int,
    post_vote: PostUpvoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await upvote_post(
        value=post_vote.value, user_id=current_user_id, post_id=post_id, db=db
    ):
        raise PostUpvoteNotFound()


@post_router.patch(path="/{post_id}/upvote", status_code=200, response_model=None)
async def toggle_post_upvote_route(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await toggle_post_upvote(user_id=current_user_id, post_id=post_id, db=db):
        raise PostUpvoteNotFound()


@post_router.delete(path="/{post_id}/upvote", status_code=200, response_model=None)
async def delete_post_upvote_route(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await delete_post_upvote(user_id=current_user_id, post_id=post_id, db=db):
        raise PostUpvoteNotFound()
