import jwt
import time
import uuid
from app.auth.exceptions import AuthenticationFailed
from app.settings import get_jwt_algorithm, get_jwt_key
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

ph = PasswordHasher()


def create_access_token(
    sub: str, jwt_key: str, jwt_algorithm: str, jwt_ttl_sec: int
) -> tuple[str, int]:
    exp = int(time.time()) + jwt_ttl_sec
    payload = {"sub": sub, "exp": exp}
    access_token = jwt.encode(payload=payload, key=jwt_key, algorithm=jwt_algorithm)
    return access_token, exp


async def create_refresh_token(
    redis: Redis, user_id: int, refresh_token_ttl_sec: int
) -> tuple[str, int]:
    refresh_token = str(uuid.uuid4())
    await redis.set(name=refresh_token, value=user_id, ex=refresh_token_ttl_sec)
    exp = int(time.time()) + refresh_token_ttl_sec
    return refresh_token, exp


def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
    jwt_key: str = Depends(get_jwt_key),
    jwt_algorithm: str = Depends(get_jwt_algorithm),
) -> dict:
    try:
        access_token = credentials.credentials
        payload = jwt.decode(jwt=access_token, key=jwt_key, algorithms=[jwt_algorithm])
        return payload
    except Exception:
        raise AuthenticationFailed()


async def verify_refresh_token(refresh_token: str, redis: Redis) -> int | None:
    user_id = await redis.get(name=refresh_token)
    return int(user_id) if user_id else None


def get_current_user_id(payload: dict = Depends(verify_access_token)) -> int:
    return int(payload["sub"])


def hash_password(password: str) -> str:
    hashed_password = ph.hash(password=password)
    return hashed_password


def verify_hashed_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hash=hashed_password, password=password)
        return True
    except VerifyMismatchError:
        return False
