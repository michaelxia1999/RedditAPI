from dataclasses import dataclass
from fastapi import Depends, FastAPI, Request
from os import environ


@dataclass
class Settings:
    ENV: str = environ["ENV"]
    DB_URL: str = environ["DB_URL"]
    REDIS_PWD = environ["REDIS_PWD"]
    REDIS_HOST = environ["REDIS_HOST"]
    REDIS_PORT = int(environ["REDIS_PORT"])
    REDIS_DB = int(environ["REDIS_DB"])
    JWT_KEY = environ["JWT_KEY"]
    JWT_ALGORITHM = environ["JWT_ALGORITHM"]
    JWT_TTL_SEC = int(environ["JWT_TTL_SEC"])
    REFRESH_TOKEN_TTL_SEC = int(environ["REFRESH_TOKEN_TTL_SEC"])
    RATE_LIMIT = int(environ["RATE_LIMIT"])


def set_settings(app: FastAPI):
    app.state.settings = Settings()


def get_settings(request: Request):
    return request.app.state.settings


def get_env(settings: Settings = Depends(get_settings)):
    return settings.ENV


def get_db_url(settings: Settings = Depends(get_settings)):
    return settings.DB_URL


def get_redis_pwd(settings: Settings = Depends(get_settings)):
    return settings.REDIS_PWD


def get_redis_host(settings: Settings = Depends(get_settings)):
    return settings.REDIS_HOST


def get_redis_port(settings: Settings = Depends(get_settings)):
    return settings.REDIS_PORT


def get_redis_db(settings: Settings = Depends(get_settings)):
    return settings.REDIS_DB


def get_jwt_key(settings: Settings = Depends(get_settings)):
    return settings.JWT_KEY


def get_jwt_algorithm(settings: Settings = Depends(get_settings)):
    return settings.JWT_ALGORITHM


def get_jwt_ttl_sec(settings: Settings = Depends(get_settings)):
    return settings.JWT_TTL_SEC


def get_refresh_token_ttl_sec(settings: Settings = Depends(get_settings)):
    return settings.REFRESH_TOKEN_TTL_SEC


def get_rate_limit(settings: Settings = Depends(get_settings)):
    return settings.RATE_LIMIT
