from app.auth.services import get_current_user_id, hash_password
from app.db.core import get_db
from app.user.exceptions import DisplayNameAlreadyExist, EmailAlreadyExist, UserNotFound
from app.user.models import UserRead, UserUpdate
from app.user.services import delete_user, display_name_exists, email_exists, get_user, update_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

user_router = APIRouter(prefix="/users", tags=["User"])


@user_router.patch(path="/me", status_code=200, response_model=UserRead)
async def update_user_route(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),
):
    if user_data.email and await email_exists(email=user_data.email, db=db):
        raise EmailAlreadyExist()

    if user_data.display_name and await display_name_exists(
        display_name=user_data.display_name, db=db
    ):
        raise DisplayNameAlreadyExist

    if user_data.password:
        user_data.password = hash_password(user_data.password)

    user = await update_user(
        user_id=current_user_id, user_data=user_data.model_dump(exclude_unset=True), db=db
    )

    if not user:
        raise UserNotFound()

    return user


@user_router.get(path="/me", status_code=200, response_model=UserRead)
async def get_user_route(
    db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)
):
    user = await get_user(user_id=current_user_id, db=db)

    if not user:
        raise UserNotFound()

    return user


@user_router.delete(path="/me", status_code=200, response_model=None)
async def delete_user_route(
    db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)
):
    if not delete_user(user_id=current_user_id, db=db):
        raise UserNotFound()
