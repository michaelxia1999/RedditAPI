import uuid
from app.exceptions import BaseError, RateLimitExceeded
from app.redis import get_redis
from fastapi import Depends, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from typing import Awaitable, Callable


async def generate_request_id_middleware(
    request: Request, next: Callable[[Request], Awaitable[Response]]
):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await next(request)
    return response


async def rate_limit_middleware(request: Request, next: Callable[[Request], Awaitable[Response]]):
    if request.client:
        host = request.client.host
        redis: Redis = request.app.state.redis
        rate_limit = request.app.state.settings.RATE_LIMIT
        count = await redis.incr(host)

        if count == 1:
            # Set expiration only when key is created
            await redis.expire(host, 60)

        if count > rate_limit:
            raise RateLimitExceeded()

    return await next(request)


async def exceptions_handler_middleware(
    request: Request, next: Callable[[Request], Awaitable[Response]]
):
    try:
        response = await next(request)
        return response

    except Exception as e:
        if isinstance(e, BaseError):
            return JSONResponse(status_code=e.status_code, content=e.content())

        if isinstance(e, RequestValidationError):
            return JSONResponse(
                status_code=400,
                content={"location": e.errors(), "message": "Request Validation Error"},
            )
        print(e)
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})
