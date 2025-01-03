from typing import Any, Dict, List, Union

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import logger
from app.dependencies import get_session, verify_api_key
from app.users.dao import FollowDAO, UserDAO
from app.users.models import User
from app.users.rb import RBCorrect, RBMe, RBUncorrect, RBUsersAdd, RBUsersUpdate
from app.users.schemas import SUserAdd

router = APIRouter(prefix="/api", tags=["users"])


@router.get("/all_users", summary="Получить всех пользователей с их токенами")
async def get_all_users(async_session_dep=Depends(get_session)) -> list[SUserAdd]:
    """
    Получение списка всех пользователей с их токенами.

    :param async_session_dep: Асинхронная сессия базы данных.
    :return: Список пользователей.
    """
    res = await UserDAO.find_all(async_session=async_session_dep)
    return [SUserAdd(**user.to_dict()) for user in res] if res else []


@router.post("/users", status_code=201, summary="Получить токен для пользователя и добавляет его в БД")
async def create_user(
    async_session_dep: AsyncSession = Depends(get_session), request_body: RBUsersAdd = Depends()
) -> SUserAdd:
    """
    Создание нового пользователя и получение его токена.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param request_body: Данные для создания пользователя.
    :return: Созданный пользователь с токеном.
    """
    res = await UserDAO.add(async_session=async_session_dep, **request_body.model_dump())
    logger.info("Создал пользователя ", **{"user": request_body.first_name})
    return SUserAdd(**res.to_dict())


@router.get("/users", summary="Залогинить пользователя по токену")
async def login_users(
    async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> SUserAdd:
    """
    Логин пользователя по токену API.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API пользователя.
    :return: Информация о пользователе.
    """
    res = await UserDAO.find_one_or_none(async_session=async_session_dep, api_key=api_key)
    if res is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден или токен недействителен.")
    return SUserAdd(**res.to_dict())


#
@router.put("/users", status_code=201, summary="Обновить данные пользователя")
async def update_users(
    async_session_dep: AsyncSession = Depends(get_session),
    api_key: str = Depends(verify_api_key),
    request_body: RBUsersUpdate = Depends(),
) -> Union[List[SUserAdd], Dict[str, Any]]:
    """
    Обновление данных пользователя по токену API.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API пользователя.
    :param request_body: Данные для обновления пользователя.
    :return: Обновленные данные пользователя или сообщение об ошибке.
    """
    res = await UserDAO.update(
        async_session=async_session_dep, **request_body.model_dump(exclude_none=True), filter_by={"api_key": api_key}
    )

    if not res:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return [SUserAdd(**user.to_dict()) for user in res]


@router.delete("/users", summary="Удалить пользователя по токену")
async def delete_users(
    async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> Dict[str, int]:
    """
    Удаление пользователя по токену API.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API пользователя.
    :return: Количество удаленных строк.
    """
    res = await UserDAO.delete(async_session=async_session_dep, api_key=api_key)
    if res == 0:
        raise HTTPException(status_code=404, detail="Пользователь не найден.")
    return {"удалено строк": res}


@router.post("/users/{id}/follow", status_code=201, summary="Подписаться на пользователя по id")
async def follow_user(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBCorrect:
    """
    Подписка на другого пользователя по его ID.

    :param id: ID пользователя на которого подписываются.
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API текущего пользователя.

    :return: Успешный ответ о подписке.
    """
    user: User | None = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await FollowDAO.add(async_session=async_session_dep, **{"user_id": user.id, "follower_id": id})
    return RBCorrect()


@router.delete("/users/{id}/follow", summary="Отписаться от пользователя по id")
async def un_follow_user(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> Union[RBCorrect, RBUncorrect]:
    """
    Отписка от другого пользователя по его ID.

    :param id: ID пользователя от которого отписываются.
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API текущего пользователя.

    :return: Успешный ответ об отписке или сообщение об ошибке.
    """
    user: User | None = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    res = await FollowDAO.delete(async_session=async_session_dep, user_id=user.id, follower_id=id)
    if res:
        return RBCorrect()
    else:
        logger.error("Не нашел пользователя с таким api_key", **{"user": api_key})
        return RBUncorrect()


@router.get("/users/me", summary="Пользователь получает информацию о своем профиле")
async def get_me(
    async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBMe | RBUncorrect:
    """
    Получение информации о текущем пользователе.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API текущего пользователя.

    :return: Информация о пользователе или сообщение об ошибке.
    """
    res = await UserDAO.user_info(async_session=async_session_dep, api_key=api_key)
    if res:
        return RBMe(**res)
    else:
        raise HTTPException(status_code=404, detail="Нет такого пользователя")


@router.get("/users/{id}", summary="Пользователь получает информацию о профиле другого пользователя")
async def get_user_by_id(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBMe | RBUncorrect:
    """
    Получение информации о другом пользователе по его ID.

    :param id: ID другого пользователя.
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: Токен API текущего пользователя.

    :return: Информация о пользователе или сообщение об ошибке.
    """
    res = await UserDAO.user_info(async_session=async_session_dep, user_id=id)
    if res.get("result"):
        return RBMe(**res)
    else:
        raise HTTPException(status_code=404, detail="Нет такого пользователя")
