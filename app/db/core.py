from fastapi import Depends, FastAPI, Request
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def set_db(app: FastAPI):
    app.state.db_engine = create_async_engine(url=app.state.settings.DB_URL, echo=False)
    app.state.db_session_factory = async_sessionmaker(bind=app.state.db_engine, autoflush=True)


async def close_db(db_engine: AsyncEngine):
    await db_engine.dispose()


async def get_db_engine(request: Request):
    return request.app.state.db_engine


async def get_db_session_factory(request: Request):
    return request.app.state.db_session_factory


async def get_db(
    session_factory: async_sessionmaker[AsyncSession] = Depends(get_db_session_factory),
):
    db = session_factory()
    try:
        yield db
        await db.commit()
    except Exception as e:
        print(e)
        await db.rollback()
        raise
    finally:
        await db.close()
