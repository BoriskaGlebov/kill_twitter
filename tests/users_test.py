import pytest


@pytest.mark.asyncio(loop_scope="session")
async def test_def_route(async_client):
    res = await async_client.get("/")
    assert res.status_code == 200


@pytest.mark.asyncio(loop_scope="session")
async def test_all_users(async_client):
    res = await async_client.get("/api/all_users")
    assert res.status_code == 200
    users = res.json()
    assert len(users) == 10
    for num, user in enumerate(users):
        assert user["api_key"] == f"api_key_{num + 1}"


@pytest.mark.asyncio(loop_scope="session")
async def test_create_user(async_client):
    user = {"first_name": "first_name_{num}", "last_name": "last_name_{num}", "api_key": "api_key_{create}"}
    # корректный запрос
    res = await async_client.post("/api/users", params=user)
    assert res.status_code == 201
    assert res.json()["api_key"] == user["api_key"]
    # попытка создать пользователя с тем же api_key
    res = await async_client.post("/api/users", params=user)
    assert res.status_code == 409
    await async_client.delete("/api/users", headers={"api-key": "api_key_{create}"})


#
@pytest.mark.asyncio(loop_scope="session")
async def test_login_users(async_client):
    x_api_key = "api_key_1"
    # некорректный api-key
    res = await async_client.get("/api/users", headers={"api-key": x_api_key[:-1]})
    assert res.status_code == 403
    assert res.json() == {
        "error_message": "Такого токена не существует, введите корректный токен",
        "error_type": "HTTPException",
        "result": False,
    }

    # корректный api-key
    res = await async_client.get("/api/users", headers={"api-key": x_api_key})
    assert res.status_code == 200
    assert res.json()["api_key"] == x_api_key


@pytest.mark.asyncio(loop_scope="session")
async def test_update_users(async_client):
    x_api_key = "api_key_1"
    params_new = {"first_name": "new", "last_name": "new", "api_key": "api_key_{update}"}
    # корректный запрос
    res = await async_client.put("/api/users", headers={"api-key": x_api_key}, params=params_new)
    assert res.status_code == 201
    assert res.json()[0]["api_key"] == params_new["api_key"]
    # корректный запрос
    res = await async_client.put("/api/users", headers={"api-key": x_api_key}, params=params_new)
    assert res.status_code == 403
    await async_client.put("/api/users", headers={"api-key": params_new["api_key"]}, params={"api_key": x_api_key})


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_users(async_client):
    user = {"first_name": "first_name_{num}", "last_name": "last_name_{num}", "api_key": "api_key_{del}"}
    await async_client.post("/api/users", params=user)
    res = await async_client.delete("/api/users", headers={"api-key": user["api_key"]})
    assert res.status_code == 200
    assert res.json() == {"удалено строк": 1}
    res = await async_client.delete("/api/users", headers={"api-key": "api_key_1"})
    assert res.status_code == 200
    assert res.json() == {"удалено строк": 1}


@pytest.mark.asyncio(loop_scope="session")
async def test_follow_user(async_client):
    user = {"first_name": "first_name_{num}", "last_name": "last_name_{num}", "api_key": "api_key_{follow}"}
    await async_client.post("/api/users", params=user)
    # корректно
    res = await async_client.post("/api/users/3/follow", headers={"api-key": user["api_key"]})
    assert res.status_code == 201
    assert res.json() == {"result": True}
    # #повтор
    res2 = await async_client.post("/api/users/3/follow", headers={"api-key": user["api_key"]})
    assert res2.status_code == 409
    await async_client.delete("/api/users", headers={"api-key": user["api_key"]})


@pytest.mark.asyncio(loop_scope="session")
async def test_un_follow_user(async_client):
    user = {"first_name": "first_name_{num}", "last_name": "last_name_{num}", "api_key": "api_key_{unfollow}"}
    await async_client.post("/api/users", params=user)
    await async_client.post("/api/users/2/follow", headers={"api-key": user["api_key"]})
    # корректно
    res = await async_client.delete("/api/users/2/follow", headers={"api-key": user["api_key"]})
    assert res.status_code == 200
    assert res.json() == {"result": True}
    await async_client.delete("/api/users", headers={"api-key": user["api_key"]})


@pytest.mark.asyncio(loop_scope="session")
async def test_get_me(async_client):
    res = await async_client.get("/api/users/me", headers={"api-key": "api_key_2"})
    assert res.status_code == 200
    assert res.json()["result"] is True


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_by_id(async_client):
    res = await async_client.get("/api/users/5", headers={"api-key": "api_key_2"})
    assert res.status_code == 200
    assert res.json()["result"] is True


#
