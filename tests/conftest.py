import asyncio
import os
from typing import AsyncGenerator

from pytest import fixture
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from app.main import app, get_session
from models.database import Base
from models.model import start_data

test_db_url = "sqlite+aiosqlite:///test_recipes.db"
test_path = os.path.abspath("test_recipes.db")
new_async_engine = create_async_engine(test_db_url, echo=False)
new_async_session = async_sessionmaker(new_async_engine, expire_on_commit=False, class_=AsyncSession)


async def get_session_override() -> AsyncGenerator:
    async with new_async_session() as session:
        yield session


app.dependency_overrides[get_session] = get_session_override


@fixture(scope="session")
def start_rows():
    return start_data()


#
@fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@fixture(scope="session")
async def prepare_database(start_rows):
    async with new_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with new_async_session() as session:
        session.add_all(start_rows)
        await session.commit()


@fixture(scope="session")
async def db_session(prepare_database):
    async with new_async_session() as session:
        yield session
        await session.rollback()
        os.remove(test_path)


#
@fixture
def api_client(db_session):
    client = TestClient(app=app)
    yield client
    client.close()


#
# #
# @fixture(scope="session")
# async def async_client(db_session):
#     async with AsyncClient(app=app, base_url="http://test") as client:
#         yield client
