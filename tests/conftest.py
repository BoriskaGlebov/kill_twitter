import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings, logger
from app.data_generate import MediaFactory, generate_follow, generate_users
from app.database import Base, async_test_session, test_engine
from app.dependencies import get_session
from app.main import app
from app.medias.dao import MediaDAO
from app.users.dao import FollowDAO, UserDAO
from migrations_script import run_alembic_command

# Настройка логирования
# logger.
# logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


async def get_session_override() -> AsyncGenerator[AsyncSession, None]:
    """
    Переопределение зависимости для получения асинхронной сессии.

    :return: Асинхронная сессия базы данных.
    """
    async with async_test_session() as session:
        yield session


# Переопределение зависимости get_session в приложении FastAPI
app.dependency_overrides[get_session] = get_session_override


# @pytest.fixture(scope="session")
# def event_loop() -> AsyncGenerator:
#     """
#     Фикстура для создания единого event loop для всех тестов.
#     Вот эта функция нужна для работы в одном event loop всех тестов
#
#     :yield: Event loop.
#     """
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def clean_database() -> None:
    """
    Фикстура для очистки базы данных перед запуском тестов.

    Эта функция очищает таблицы в базе данных, чтобы обеспечить чистое состояние для тестов.
    """
    if os.path.split(os.getcwd())[1] == "tests":
        run_alembic_command("cd ..; alembic -x db=test upgrade head;alembic -x db=test current")
    elif os.path.split(os.getcwd())[1] == "kill_twitter":
        run_alembic_command("alembic -x db=test upgrade head;alembic -x db=test current")

    async with async_test_session() as session:
        # Пример для PostgreSQL
        await session.execute(text("TRUNCATE TABLE follows RESTART IDENTITY CASCADE;"))  # Пример для PostgreSQL
        # await session.execute(text("TRUNCATE TABLE likes RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE medias RESTART IDENTITY CASCADE;"))
        # await session.execute(text("TRUNCATE TABLE tweetmedias RESTART IDENTITY CASCADE;"))
        # await session.execute(text("TRUNCATE TABLE tweets RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        await session.commit()
    #
    logger.error("Database cleaned.")


@pytest.fixture(scope="session")
async def test_db(async_client):
    """аасинхронную сессию возвращает"""
    engine = test_engine  # Используем in-memory SQLite базу данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы

    sessionlocal = async_test_session

    async with sessionlocal() as session:
        users = generate_users(10)
        follows = generate_follow(10)
        [await UserDAO.add(async_session=session, **user.to_dict()) for user in users]
        [await FollowDAO.add(async_session=session, **follow.to_dict()) for follow in follows]
        [await MediaDAO.add(session, **MediaFactory().to_dict()) for _ in range(1, 21)]
        yield session  # Возвращаем сессию для использования в тестах


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # users = [
        #     {"first_name": f"new_{num + 1}", "last_name": f"new_{num + 1}", "api_key": f"api_key_{num + 1}"}
        #     for num in range(10)
        # ]
        # for user in users:
        #     res = await client.post("/api/users", params=user)
        #     assert res.status_code == 201
        # # Добавляю подписчиков
        # for follow in range(10):
        #     for _ in range(3):
        #
        #         user_id = randint(1, 10)
        #         if user_id == follow + 1:
        #             continue
        #         res = await client.post(f"/api/users/{user_id}/follow", headers={"api-key": f"api_key_{follow + 1}"})
        #         assert res.status_code in (201, 409)
        yield client


@pytest.fixture(scope="session")
def config():
    """
    Фикстура для тестов конфигурации.

    :yield: Настройки приложения.
    """
    settings = get_settings()
    yield settings
