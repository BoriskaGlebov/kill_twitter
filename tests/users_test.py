import pytest

from app.config import logger
from app.data_generate import UserFactory
from app.users.dao import UserDAO


@pytest.mark.asyncio(loop_scope="session")
async def test_def_route(async_client):
    """Тест базового роута"""
    res = await async_client.get("/")
    assert res.status_code == 200
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_all_users(async_client, test_db):
    """Поверка получения всех пользователей"""
    res = await async_client.get("/api/all_users")
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 10
    users_db = await UserDAO.find_all(async_session=test_db)
    for num, user in enumerate(users):
        assert user["api_key"] == users_db[num].api_key
        logger.info("OK", user=user["first_name"])
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(async_client):
    """Проверка создания пользователя"""
    user = UserFactory()
    # корректный запрос
    res = await async_client.post("/api/users", params=user.to_dict())
    assert res.status_code == 201
    assert res.json()["api_key"] == user.api_key
    # попытка создать пользователя с тем же api_key
    res = await async_client.post("/api/users", params=user.to_dict())
    assert res.status_code == 409
    assert res.json()["result"] is False
    # попытка добавить полльзователя с ошибкой заполнения
    new_user: dict = user.to_dict().copy()
    del new_user["first_name"]
    res = await async_client.post("/api/users", params=new_user)
    assert res.status_code == 400
    assert res.json()["result"] is False
    # Удаляю пользователя
    del_res = await async_client.delete("/api/users", headers={"api-key": user.api_key})
    assert del_res.status_code == 200
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_login_users(async_client, test_db):
    """Проверка авторизации пользователя"""
    x_api_key = (await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=2)).api_key
    # некорректный api-key
    res = await async_client.get("/api/users", headers={"api-key": x_api_key[:-1]})
    assert res.status_code == 403
    assert res.json()["result"] is False
    # без header
    res2 = await async_client.get("/api/users")
    assert res2.status_code == 403
    assert res2.json()["result"] is False
    # # корректный api-key
    res = await async_client.get("/api/users", headers={"api-key": x_api_key})
    assert res.status_code == 200
    assert res.json()["api_key"] == x_api_key
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_update_users(async_client, test_db):
    """Проверка обновления пользователя"""
    x_api_key = (await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=2)).api_key
    params_new = UserFactory()
    # корректный запрос
    res = await async_client.put("/api/users", headers={"api-key": x_api_key}, params=params_new.to_dict())
    assert res.status_code == 201
    assert res.json()[0]["api_key"] == params_new.to_dict()["api_key"]
    assert res.json()[0]["api_key"] != x_api_key
    # корректный запрос
    res2 = await async_client.put("/api/users", headers={"api-key": x_api_key}, params=params_new.to_dict())
    assert res2.status_code == 403
    assert res2.json()["result"] is False
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_users(async_client):
    """Проверка удаления пользователя"""
    user = UserFactory()
    await async_client.post("/api/users", params=user.to_dict())
    res = await async_client.delete("/api/users", headers={"api-key": user.api_key})
    assert res.status_code == 200
    assert res.json() == {"удалено строк": 1}
    res2 = await async_client.delete("/api/users", headers={"api-key": user.api_key})
    assert res2.status_code == 403
    assert res2.json()["result"] is False
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_follow_user(async_client):
    """Проверка подписи на пользователя"""
    user = UserFactory()
    await async_client.post("/api/users", params=user.to_dict())
    # корректно
    res = await async_client.post("/api/users/3/follow", headers={"api-key": user.api_key})
    assert res.status_code == 201
    assert res.json() == {"result": True}
    # #повтор
    res2 = await async_client.post("/api/users/3/follow", headers={"api-key": user.api_key})
    assert res2.status_code == 409
    assert res2.json()["result"] is False
    await async_client.delete("/api/users", headers={"api-key": user.api_key})
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_un_follow_user(async_client):
    """Проверка отписки от пользователя"""
    user = UserFactory()
    await async_client.post("/api/users", params=user.to_dict())
    await async_client.post("/api/users/2/follow", headers={"api-key": user.api_key})
    # корректно
    res = await async_client.delete("/api/users/2/follow", headers={"api-key": user.api_key})
    assert res.status_code == 200
    assert res.json() == {"result": True}
    res = await async_client.delete("/api/users/2/follow", headers={"api-key": user.api_key})
    assert res.status_code == 200
    assert res.json() == {"result": False}
    await async_client.delete("/api/users", headers={"api-key": user.api_key})
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me(async_client, test_db):
    """Проверка информации пользователя"""
    user = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=4)
    res = await async_client.get("/api/users/me", headers={"api-key": user.api_key})
    assert res.status_code == 200
    assert res.json()["result"] is True
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id(async_client, test_db):
    """Проверка информации любого пользователя"""
    user = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=4)
    res = await async_client.get("/api/users/5", headers={"api-key": user.api_key})
    assert res.status_code == 200
    assert res.json()["result"] is True
    res2 = await async_client.get("/api/users/500", headers={"api-key": user.api_key})
    assert res2.status_code == 404
    assert res2.json()["result"] is False
    logger.info("OK")
