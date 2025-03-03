from app.db.core import get_db_engine
from app.db.services import create_tables, disable_extensions, drop_tables, enable_extensions
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncEngine

database_router = APIRouter(prefix="/db", tags=["DB"])


@database_router.delete(path="")
async def drop_databaset_route(db_engine: AsyncEngine = Depends(get_db_engine)):
    await drop_tables(db_engine=db_engine)


@database_router.put(path="")
async def reset_database_route(db_engine: AsyncEngine = Depends(get_db_engine)):
    await drop_tables(db_engine=db_engine)
    await disable_extensions(db_engine=db_engine)

    await create_tables(db_engine=db_engine)
    await enable_extensions(db_engine=db_engine)


@database_router.post(path="/extensions")
async def enable_extensions_route(db_engine: AsyncEngine = Depends(get_db_engine)):
    await enable_extensions(db_engine=db_engine)


@database_router.delete(path="/extensions")
async def disable_extensions_route(db_engine: AsyncEngine = Depends(get_db_engine)):
    await disable_extensions(db_engine=db_engine)
