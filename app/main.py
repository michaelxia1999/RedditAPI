from app.config import set_exception_handlers, set_middlewares, set_routers, set_swaggerui
from app.db.core import close_db, set_db
from app.redis import close_redis, set_redis
from app.settings import set_settings
from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis(redis=app.state.redis)
    await close_db(db_engine=app.state.db_engine)


def create_app():
    app = FastAPI(lifespan=lifespan)
    set_exception_handlers(app=app)
    set_middlewares(app=app)
    set_routers(app=app)
    set_swaggerui(app=app)
    set_settings(app=app)
    set_db(app=app)
    set_redis(app=app)

    return app


app = create_app()
