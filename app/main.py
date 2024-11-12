import os.path
from contextlib import asynccontextmanager
from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import IntegrityError
from starlette.responses import HTMLResponse

from app.config import settings
from app.data_generate import generate_follow, generate_users
from app.database import Base, engine
from app.dependencies import get_session
from app.exceptions.exceptions_methods import (
    http_exception_handler,
    integrity_error_exception_handler,
    validation_exception_handler,
)

# from app.medias.router import router as router_medias
# from app.medias.dao import MediaDAO
# from app.tweets.dao import TweetDAO, LikeDAO, TweetMediaDAO
# from app.tweets.router import router as router_tweets
from app.users.dao import FollowDAO, UserDAO
from app.users.router import router as router_users
from migrations_script import run_alembic_command

# API теги и их описание
tags_metadata: List[Dict[str, Any]] = [
    {
        "name": "users",
        "description": "Получаются данные по пользователям",
    },
    {
        "name": "tweets",
        "description": "Операции с Твитами",
        "externalDocs": {
            "description": "Ссылка на документацию",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
    {"name": "medias", "description": "Работа с медиафайлами"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Действия перед запуском приложения
    :param app:
    :return:
    """
    print("Перед первым запуском необходимо убедиться в актуальности версии миграции")
    if os.path.split(os.getcwd())[1] == "app":
        run_alembic_command("cd ..; alembic upgrade head;alembic current")
    elif os.path.split(os.getcwd())[1] == "kill_twitter":
        run_alembic_command("alembic upgrade head;alembic current")
    # run_alembic_command(f'alembic current')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async for session in get_session():
        await UserDAO.add(session, **{"first_name": "Test_name", "last_name": "Test_surname", "api_key": "test"})
        [await UserDAO.add(session, **user.to_dict()) for user in generate_users(100)]
        [await FollowDAO.add(session, **follow.to_dict()) for follow in generate_follow(100)]
    yield

    # async for session in get_session():
    #     async def add_user(user_data):
    #         async with get_session() as session:
    #             return await UserDAO.add(session, **user_data.to_dict())
    #
    #     async def add_follow(follow_data):
    #         async with get_session() as session:
    #             return await FollowDAO.add(session, **follow_data.to_dict())
    #     # Параллельное добавление пользователей и подписок с использованием отдельных сессий
    #     users = await asyncio.gather(*(add_user(user) for user in generate_users(100)))
    #     follows = await asyncio.gather(*(add_follow(follow) for follow in generate_follow(100)))
    #     test_user = await UserDAO.add(session, **{'first_name': "Test_name",
    #                                               "last_name": "Test_surname",
    #                                               "api_key": "test"})
    # users = await asyncio.gather(*(UserDAO.add(session, **user.to_dict()) for user in generate_users(100)))
    # follows = await asyncio.gather(*(FollowDAO.add(session, **follow.to_dict()) for follow in generate_follow(100)))
    # #         # tweets = [await TweetDAO.add(session, **TweetFactory().to_dict()) for _ in range(100)]
    # #         # likes = [await LikeDAO.add(session, **like.to_dict()) for like in generate_likes(100)]
    # #         # medias = [await MediaDAO.add(session, **MediaFactory().to_dict()) for _ in range(1, 21)]
    # #         # tweet_media = [await TweetMediaDAO.add(session, **inst.to_dict()) for inst in generate_tweet_media(100)]
    # #     # Инициализация базы данных при старте приложения
    yield  # Здесь можно добавить код для завершения работы приложения (если нужно)


app = FastAPI(
    debug=True,
    title="Kill Twitter API",
    summary="Реализовать бэкенд сервиса микроблогов.",
    description="""
---
# Kill Twitter API

Для корпоративного сервиса микроблогов необходимо реализовать бэкенд
приложения. Поскольку это корпоративная сеть, то функционал будет урезан
относительно оригинала. Как правило, описание сервиса лучше всего дать
через функциональные требования, то есть заказчик формулирует простымязыком,
что система должна уметь делать. Или что пользователь хочет делать
с системой. И вот что должен уметь делать наш сервис:
---
## Функциональные требования:
1. Пользователь может добавить новый твит.
2. Пользователь может удалить свой твит.
3. Пользователь может зафоловить другого пользователя.
4. Пользователь может отписаться от другого пользователя.
5. Пользователь может отмечать твит как понравившийся.
6. Пользователь может убрать отметку «Нравится».
7. Пользователь может получить ленту из твитов отсортированных в
порядке убывания по популярности от пользователей, которых он
фоловит.
8. Твит может содержать картинку.

*Заметим, что требования регистрации пользователя нет: это корпоративная
сеть и пользователи будут создаваться не нами. Но нам нужно уметь отличать
одного пользователя от другого. Об этом поговорим чуть позже.
Также систему описывают через список нефункциональных требований, то
есть список того, как система должна выполнять функциональные
требования.*
---
## Нефункциональные требования:
1. Систему должно быть просто развернуть через Docker Compose.
2. Система не должна терять данные пользователя между запусками.
3. Все ответы сервиса должны быть задокументированы через Swagger.
Документация должна быть доступна в момент запуска приложения.
Также не забудьте оформить развёрнутый README с описанием
проекта и инструкцией по запуску приложения.

---

""",
    openapi_tags=tags_metadata,
    contact={
        "name": "Boriska Glebov",
        "url": "http://localhost:8000/docs",
        "email": "BorisTheBlade.glebov@yandex.ru",
    },
    lifespan=lifespan,
)

app.include_router(router_users)
# app.include_router(router_tweets)
# app.include_router(router_medias)

# Mount the Prometheus metrics endpoint
instrumentator = Instrumentator().instrument(app).expose(app)

# для тестовой разработки подключение статических файлов
app.mount("/static", StaticFiles(directory=settings.static_path()), name="static")
templates = Jinja2Templates(directory=settings.template_path())

# Определение обработчиков исключений
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(IntegrityError, integrity_error_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore


@app.get("/", response_class=HTMLResponse)
async def hello_world(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


#
# @app.get('/test')
# async def get_test(id: int):
#     try:
#         result = 1 / id
#     except ZeroDivisionError as e:
#         print(e)
#         raise HTTPException(status_code=400, detail=e)
#     return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
