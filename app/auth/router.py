from app.auth.exceptions import AuthenticationFailed
from app.auth.models import SignInCredentials, SignInResponse, TokenIn, TokenOut
from app.auth.services import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_refresh_token,
)
from app.db.core import get_db
from app.redis import get_redis
from app.settings import get_jwt_algorithm, get_jwt_key, get_jwt_ttl_sec, get_refresh_token_ttl_sec
from app.user.exceptions import DisplayNameAlreadyExist, EmailAlreadyExist, UsernameAlreadyExist
from app.user.models import UserCreate
from app.user.services import (
    create_user,
    display_name_exists,
    email_exists,
    get_user_id_by_credentials,
    username_exists,
)
from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(path="/sign-up", status_code=201, response_model=SignInResponse)
async def sign_up_route(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    jwt_key: str = Depends(get_jwt_key),
    jwt_algorithm: str = Depends(get_jwt_algorithm),
    jwt_ttl_sec: int = Depends(get_jwt_ttl_sec),
    refresh_token_ttl_sec: int = Depends(get_refresh_token_ttl_sec),
    redis: Redis = Depends(get_redis),
):
    if await username_exists(username=user_data.username, db=db):
        raise UsernameAlreadyExist()

    if await email_exists(email=user_data.email, db=db):
        raise EmailAlreadyExist()

    if await display_name_exists(display_name=user_data.display_name, db=db):
        raise DisplayNameAlreadyExist

    user = await create_user(
        username=user_data.username,
        password=hash_password(user_data.password),
        email=user_data.email,
        display_name=user_data.display_name,
        avatar=user_data.avatar,
        db=db,
    )

    access_token, access_exp = create_access_token(
        sub=str(user.id), jwt_key=jwt_key, jwt_algorithm=jwt_algorithm, jwt_ttl_sec=jwt_ttl_sec
    )

    refresh_token, refresh_exp = await create_refresh_token(
        redis=redis, user_id=user.id, refresh_token_ttl_sec=refresh_token_ttl_sec
    )
    return {
        "access_token": {"token": access_token, "exp": access_exp},
        "refresh_token": {"token": refresh_token, "exp": refresh_exp},
    }


@auth_router.post(path="/sign-in", status_code=200, response_model=SignInResponse)
async def sign_in_route(
    credentials: SignInCredentials,
    db: AsyncSession = Depends(get_db),
    jwt_key: str = Depends(get_jwt_key),
    jwt_algorithm: str = Depends(get_jwt_algorithm),
    jwt_ttl_sec: int = Depends(get_jwt_ttl_sec),
    refresh_token_ttl_sec: int = Depends(get_refresh_token_ttl_sec),
    redis: Redis = Depends(get_redis),
):
    user_id = await get_user_id_by_credentials(
        username=credentials.username, password=credentials.password, db=db
    )

    if not user_id:
        raise AuthenticationFailed()

    access_token, access_exp = create_access_token(
        sub=str(user_id), jwt_key=jwt_key, jwt_algorithm=jwt_algorithm, jwt_ttl_sec=jwt_ttl_sec
    )

    refresh_token, refresh_exp = await create_refresh_token(
        redis=redis, user_id=user_id, refresh_token_ttl_sec=refresh_token_ttl_sec
    )
    return {
        "access_token": {"token": access_token, "exp": access_exp},
        "refresh_token": {"token": refresh_token, "exp": refresh_exp},
    }


@auth_router.post(path="/sign-out", status_code=200, response_model=None)
async def sign_out_route(token: TokenIn, redis: Redis = Depends(get_redis)):
    deleted = await redis.delete(token.token)

    if not deleted:
        raise AuthenticationFailed()


@auth_router.post(path="/refresh", status_code=200, response_model=TokenOut)
async def refresh_access_token_route(
    token: TokenIn,
    jwt_key: str = Depends(get_jwt_key),
    jwt_algorithm: str = Depends(get_jwt_algorithm),
    jwt_ttl_sec: int = Depends(get_jwt_ttl_sec),
    redis: Redis = Depends(get_redis),
):
    user_id = await verify_refresh_token(refresh_token=token.token, redis=redis)

    if not user_id:
        raise AuthenticationFailed()

    access_token, exp = create_access_token(
        sub=str(user_id), jwt_key=jwt_key, jwt_algorithm=jwt_algorithm, jwt_ttl_sec=jwt_ttl_sec
    )

    return {"token": access_token, "exp": exp}


@auth_router.delete(path="/redis", status_code=200, response_model=None)
async def reset_redis_route(redis: Redis = Depends(get_redis)):
    await redis.flushdb()
