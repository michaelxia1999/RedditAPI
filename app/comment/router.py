from app.auth.services import get_current_user_id
from app.comment.exceptions import CommentNotFound, CommentUpvoteNotFound
from app.comment.models import (
    CommentCreate,
    CommentRead,
    CommentReads,
    CommentUpdate,
    CommentUpvoteCreate,
)
from app.comment.services import (
    delete_comment,
    delete_comment_upvote,
    get_comment,
    get_comment_replies,
    get_comments,
    submit_comment,
    toggle_comment_upvote,
    update_comment,
    upvote_comment,
)
from app.db.core import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

comment_router = APIRouter(
    prefix="/subreddits/{subreddit_id}/posts/{post_id}/comments", tags=["Comment"]
)


@comment_router.post(path="", status_code=201, response_model=CommentRead)
async def submit_comment_route(
    post_id: int,
    comment_data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    comment_id = await submit_comment(
        body=[data.model_dump() for data in comment_data.body],
        post_id=post_id,
        parent_comment_id=comment_data.parent_comment_id,
        user_id=current_user_id,
        db=db,
    )

    comment = await get_comment(comment_id=comment_id, db=db)

    if not comment:
        raise CommentNotFound()

    comment = comment._asdict()
    comment.update(comment.pop("Comment").to_dict())
    return comment


@comment_router.get(path="/{comment_id}", status_code=200, response_model=CommentRead)
async def get_comment_route(comment_id: int, db: AsyncSession = Depends(get_db)):
    comment = await get_comment(comment_id=comment_id, db=db)
    if not comment:
        raise CommentNotFound()

    comment = comment._asdict()
    comment.update(comment.pop("Comment").to_dict())
    return comment


@comment_router.delete(path="/{comment_id}", status_code=200, response_model=None)
async def delete_comment_route(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await delete_comment(comment_id=comment_id, user_id=current_user_id, db=db):
        raise CommentNotFound()


@comment_router.patch(path="/{comment_id}", status_code=200, response_model=CommentRead)
async def update_comment_route(
    comment_id: int,
    comment_data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await update_comment(
        comment_id=comment_id,
        user_id=current_user_id,
        comment_data=comment_data.model_dump(exclude_unset=True),
        db=db,
    ):
        raise CommentNotFound()

    comment = await get_comment(comment_id=comment_id, db=db)
    if not comment:
        raise CommentNotFound()

    comment = comment._asdict()
    comment.update(comment.pop("Comment").to_dict())
    return comment


@comment_router.get(path="", status_code=200, response_model=CommentReads)
async def get_comments_route(
    post_id: int,
    score_cursor: int | None = None,
    id_cursor: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await get_comments(
        post_id=post_id, score_cursor=score_cursor, id_cursor=id_cursor, db=db
    )

    if result is None:
        raise CommentNotFound()

    comments, next_score_cursor, next_id_cursor = result

    res = {"comments": [], "score_cursor": next_score_cursor, "id_cursor": next_id_cursor}

    for comment in comments:
        comment = comment._asdict()
        comment.update(comment.pop("Comment").to_dict())
        res["comments"].append(comment)

    return res


@comment_router.get(path="/{comment_id}/replies", status_code=200, response_model=CommentReads)
async def get_comment_replies_route(
    comment_id: int,
    score_cursor: int | None = None,
    id_cursor: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    result = await get_comment_replies(
        comment_id=comment_id, score_cursor=score_cursor, id_cursor=id_cursor, db=db
    )

    if result is None:
        raise CommentNotFound()

    comments, next_score_cursor, next_id_cursor = result

    res = {"comments": [], "score_cursor": next_score_cursor, "id_cursor": next_id_cursor}

    for comment in comments:
        comment = comment._asdict()
        comment.update(comment.pop("Comment").to_dict())
        res["comments"].append(comment)

    return res


@comment_router.post(path="/{comment_id}/upvote", status_code=201, response_model=None)
async def upvote_comment_route(
    comment_id: int,
    comment: CommentUpvoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await upvote_comment(
        user_id=current_user_id, comment_id=comment_id, value=comment.value, db=db
    ):
        raise CommentNotFound()


@comment_router.patch(path="/{comment_id}/upvote", status_code=200, response_model=None)
async def toggle_comment_upvote_route(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await toggle_comment_upvote(user_id=current_user_id, comment_id=comment_id, db=db):
        raise CommentUpvoteNotFound()


@comment_router.delete(path="/{comment_id}/upvote", status_code=200, response_model=None)
async def delete_comment_upvote_route(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if not await delete_comment_upvote(user_id=current_user_id, comment_id=comment_id, db=db):
        raise CommentUpvoteNotFound()
