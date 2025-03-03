from app.db.schema import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def create_tables(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def enable_extensions(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))


async def disable_extensions(db_engine: AsyncEngine):
    async with db_engine.begin() as conn:
        await conn.execute(text("DROP EXTENSION IF EXISTS pg_trgm;"))
