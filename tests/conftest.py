import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings, logger
from app.data_generate import (
    MediaFactory,
    TweetFactory,
    generate_follow,
    generate_likes,
    generate_tweet_media,
    generate_users,
)
from app.database import Base, async_test_session, test_engine
from app.dependencies import get_session
from app.main import app
from app.medias.dao import MediaDAO
from app.tweets.dao import LikeDAO, TweetDAO, TweetMediaDAO
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
        await session.execute(text("TRUNCATE TABLE follows RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE likes RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE medias RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE tweetmedias RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE tweets RESTART IDENTITY CASCADE;"))
        await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
        await session.commit()
    #
    logger.error("Database cleaned.")


@pytest.fixture(scope="session")
async def test_db(async_client):
    """Асинхронную сессию возвращает."""
    engine = test_engine  # Используем in-memory SQLite базу данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Создаем таблицы

    sessionlocal = async_test_session

    async with sessionlocal() as session:
        generate_users(10)
        generate_follow(10)
        await UserDAO.add(session, **{"first_name": "Test_name", "last_name": "Test_surname", "api_key": "test"})
        [await UserDAO.add(session, **user.to_dict()) for user in generate_users(100)]
        [await FollowDAO.add(session, **follow.to_dict()) for follow in generate_follow(100)]
        [await MediaDAO.add(session, **MediaFactory().to_dict()) for _ in range(1, 21)]
        [await TweetDAO.add(session, **TweetFactory().to_dict()) for _ in range(100)]
        [await LikeDAO.add(session, **like.to_dict()) for like in generate_likes(100)]
        [await TweetMediaDAO.add(session, **inst.to_dict()) for inst in generate_tweet_media(100)]
        yield session  # Возвращаем сессию для использования в тестах


@pytest_asyncio.fixture(scope="session")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Асинхронный клиент для тестирования.

    Эта фикстура создает асинхронный HTTP-клиент, который используется для
    выполнения запросов к приложению в тестах. Клиент инициализируется
    с использованием ASGITransport и может быть использован для
    отправки запросов к тестируемому приложению.

    :yield: Асинхронный клиент HTTP, который можно использовать в тестах.
    :rtype: AsyncClient
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
def config():
    """
    Фикстура для тестов конфигурации.

    :yield: Настройки приложения.
    """
    settings = get_settings()
    yield settings
