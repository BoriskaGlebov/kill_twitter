import logging

import pytest

from app.config import get_settings

#
# from app.main import app
# from app.database import async_test_session, Base, test_engine
# from app.dependencies import get_session


logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")


# async def get_session_override() -> AsyncGenerator:
#     async with async_test_session() as session:
#         yield session


# app.dependency_overrides[get_session] = get_session_override

#
# @pytest.fixture(scope="session")
# def event_loop():
#     """Вот эта функция нужна для работы в одном event loop всех тестов"""
#     loop = asyncio.get_event_loop()
#     yield loop
#     loop.close()
#
#
# @pytest_asyncio.fixture(scope='session', autouse=True)
# async def clean_database():
#     # Здесь вы можете добавить логику для очистки базы данных
#     async with async_test_session() as session:
#         # Пример для PostgreSQL
#         await session.execute(text("TRUNCATE TABLE follows RESTART IDENTITY CASCADE;"))  # Пример для PostgreSQL
#         await session.execute(text("TRUNCATE TABLE likes RESTART IDENTITY CASCADE;"))
#         await session.execute(text("TRUNCATE TABLE medias RESTART IDENTITY CASCADE;"))
#         await session.execute(text("TRUNCATE TABLE tweetmedias RESTART IDENTITY CASCADE;"))
#         await session.execute(text("TRUNCATE TABLE tweets RESTART IDENTITY CASCADE;"))
#         await session.execute(text("TRUNCATE TABLE users RESTART IDENTITY CASCADE;"))
#         await session.commit()
#
#     logging.error("Database cleaned.")
#
#
# @pytest_asyncio.fixture(scope='session')
# async def async_client(event_loop):
#     async with AsyncClient(
#             app=app, base_url="http://test"
#     ) as client:
#         users = [{'first_name': f'new_{num + 1}',
#                   'last_name': f'new_{num + 1}',
#                   'api_key': f'api_key_{num + 1}'}
#                  for num in range(10)]
#         for user in users:
#             res = await client.post('/api/users', params=user)
#             assert res.status_code == 201
#         # Добавляю подписчиков
#         for follow in range(10):
#             for _ in range(3):
#
#                 user_id = randint(1, 10)
#                 if user_id == follow + 1:
#                     continue
#                 res = await client.post(f'/api/users/{user_id}/follow',
#                                         headers={'api-key': f'api_key_{follow + 1}'})
#                 assert res.status_code in (201, 404)
#         yield client
#


@pytest.fixture(scope="session")
def config():
    """Фикстура для тестов конфигурации"""
    settings = get_settings()
    yield settings
