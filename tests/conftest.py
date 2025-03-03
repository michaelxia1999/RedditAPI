import pytest_asyncio
from app.db.core import get_db
from app.db.services import create_tables, drop_tables
from app.main import create_app, lifespan
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app_instance():
    app = create_app()
    async with lifespan(app=app):
        yield app


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def redis_teardown(app_instance: FastAPI):
    yield
    await app_instance.state.redis.flushdb()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_tables_setup(app_instance: FastAPI):
    await create_tables(db_engine=app_instance.state.db_engine)
    yield
    await drop_tables(db_engine=app_instance.state.db_engine)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def db_session(app_instance: FastAPI):
    session = app_instance.state.db_session_factory()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def db_rollback(db_session: AsyncSession):
    yield
    await db_session.rollback()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def override_dependencies(app_instance: FastAPI, db_session: AsyncSession):
    app_instance.dependency_overrides[get_db] = lambda: db_session
    yield
    app_instance.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_client(
    app_instance: FastAPI, override_dependencies, db_tables_setup, redis_teardown
):
    async with AsyncClient(
        transport=ASGITransport(app=app_instance), base_url="http://test"
    ) as client:
        yield client
        await client.aclose()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def created_user(test_client: AsyncClient):
    json = {
        "username": "mike",
        "password": "1234",
        "email": "mike@gmail.com",
        "display_name": "mike",
        "avatar": "s3.avatar",
    }
    response = await test_client.post("/auth/sign-up", json=json)
    assert response.status_code == 201
    return [
        response.json()["access_token"]["token"],
        response.json()["refresh_token"]["token"],
        json,
    ]
