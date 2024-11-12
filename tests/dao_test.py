import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.users.dao import UserDAO


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_all(test_db):
    """Проверка получения всех пользователей"""
    res = await UserDAO.find_all(async_session=test_db)
    assert len(res) == 10


@pytest.mark.parametrize("data_id, expected", [(num + 1, num + 1) for num in range(10)])
@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_by_id(test_db, data_id, expected):
    """Проверка получения пользователя по id"""
    res = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=data_id)
    assert res.id == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_by_id_none(test_db):
    """Проверка получения пользователя по id,но вернет NONE"""
    res = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=0)
    assert res is None


@pytest.mark.parametrize(
    "parameter,input_value, expected",
    [("id", 1, 1), ("first_name", "new_2", 2), ("last_name", "new_3", 3), ("api_key", "api_key_4", 4)],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none(test_db, parameter, input_value, expected):
    """Проверка получения пользователя по параметру"""
    res = await UserDAO.find_one_or_none(async_session=test_db, **{parameter: input_value})
    assert res.id == expected


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_none(test_db):
    """Проверка получения пользователя по параметру, но вернет NONE"""
    res = await UserDAO.find_one_or_none(async_session=test_db, **{"id": 0})
    assert res is None


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_add(test_db):
    """Проверка добавления пользователя и возможные ошибки"""
    test_user = {"first_name": f"new_{100 + 1}", "last_name": f"new_{100 + 1}", "api_key": f"api_key_{100 + 1}"}
    add_user = await UserDAO.add(async_session=test_db, **test_user)
    assert add_user.to_dict()["first_name"] == "new_101"
    with pytest.raises(SQLAlchemyError):
        await UserDAO.add(async_session=test_db, **test_user)
        bad_user = {"first_name": f"new_{100 + 1}", "api_key": f"api_key_{100 + 1}"}
        await UserDAO.add(async_session=test_db, **bad_user)
    del_user = await UserDAO.delete(async_session=test_db, first_name="new_101")
    assert del_user == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_update(test_db):
    test_user = {"first_name": f"new_{100 + 1}", "last_name": f"new_{100 + 1}", "api_key": f"api_key_{100 + 1}"}
    add_user = await UserDAO.add(async_session=test_db, **test_user)
    assert add_user.to_dict()["first_name"] == "new_101"
    test_user2 = {"first_name": f"new_{100 + 2}"}
    update_user2 = await UserDAO.update(async_session=test_db, filter_by={"api_key": "api_key_101"}, **test_user2)
    assert update_user2[0].to_dict()["first_name"] == "new_102"
    update_user_bad_key = await UserDAO.update(
        async_session=test_db, filter_by={"api_key": "api_key_1000"}, **test_user2
    )
    assert len(update_user_bad_key) == 0
    with pytest.raises(SQLAlchemyError):
        # Конфликт api key уникальность
        await UserDAO.update(async_session=test_db, filter_by={"api_key": "api_key_1"}, **{"api_key": "api_key_2"})
    del_user = await UserDAO.delete(async_session=test_db, first_name="new_102")
    assert del_user == 1


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_delete(test_db):
    test_user = {"first_name": f"new_{100 + 1}", "last_name": f"new_{100 + 1}", "api_key": f"api_key_{100 + 1}"}
    await UserDAO.add(async_session=test_db, **test_user)
    del_user = await UserDAO.delete(async_session=test_db, first_name="new_101")
    assert del_user == 1
    # del_user = await UserDAO.delete(async_session=test_db, delete_all=True)
    # assert del_user == 10
    # all_users_db = await UserDAO.find_all(async_session=test_db)
    # assert len(all_users_db) == 0
