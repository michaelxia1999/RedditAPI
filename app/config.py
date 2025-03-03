from app.auth.router import auth_router
from app.comment.router import comment_router
from app.db.router import database_router
from app.exception_handlers import handle_request_validation_error
from app.middlewares import (
    exceptions_handler_middleware,
    generate_request_id_middleware,
    rate_limit_middleware,
)
from app.post.router import post_router
from app.subreddit.router import subreddit_router
from app.user.router import user_router
from fastapi import APIRouter, FastAPI
from fastapi.exceptions import RequestValidationError


def set_exception_handlers(app: FastAPI):
    app.exception_handler(RequestValidationError)(handle_request_validation_error)


def set_middlewares(app: FastAPI):
    app.middleware("http")(rate_limit_middleware)
    app.middleware("http")(generate_request_id_middleware)
    app.middleware("http")(exceptions_handler_middleware)  # should be placed last


def set_routers(app: FastAPI):
    main_router = APIRouter()
    main_router.include_router(router=auth_router)
    main_router.include_router(router=user_router)
    main_router.include_router(router=database_router)
    main_router.include_router(router=subreddit_router)
    main_router.include_router(router=post_router)
    main_router.include_router(router=comment_router)
    app.include_router(router=main_router)


def set_swaggerui(app: FastAPI):
    app.title = "Reddit API Clone"
    app.swagger_ui_parameters = {"defaultModelsExpandDepth": -1}

    schema = app.openapi()

    if "components" in schema and "schemas" in schema["components"]:
        schema["components"]["schemas"].pop("HTTPValidationError", None)
        schema["components"]["schemas"].pop("ValidationError", None)

    for path in schema["paths"].values():
        for method in path.values():
            method["summary"] = ""
            method["responses"].pop("422", None)

    app.openapi_schema = schema
