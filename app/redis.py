from fastapi import FastAPI, Request
from redis.asyncio import Redis


def set_redis(app: FastAPI):
    app.state.redis = Redis(host=app.state.settings.REDIS_HOST, port=app.state.settings.REDIS_PORT, db=app.state.settings.REDIS_DB, password=app.state.settings.REDIS_PWD, decode_responses=True)


def get_redis(request: Request):
    return request.app.state.redis


async def close_redis(redis: Redis):
    await redis.aclose()