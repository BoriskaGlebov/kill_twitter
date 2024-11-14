import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.config import logger
from app.data_generate import UserFactory
from app.users.dao import UserDAO


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_all(test_db):
    """Проверка получения всех пользователей"""
    res = await UserDAO.find_all(async_session=test_db)
    assert len(res) == 10
    logger.info("ОК")


@pytest.mark.parametrize("data_id, expected", [(num + 1, num + 1) for num in range(10)])
@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_by_id(test_db, data_id, expected):
    """Проверка получения пользователя по id"""
    res = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=data_id)
    assert res.id == expected
    logger.info("ОК")


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_by_id_none(test_db):
    """Проверка получения пользователя по id,но вернет NONE"""
    res = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=0)
    assert res is None
    logger.info("ОК")


# @pytest.mark.parametrize(
#     "parameter,input_value, expected",
#     [("id", 1, 1), ("first_name", "new_2", 2), ("last_name", "new_3", 3), ("api_key", "api_key_4", 4)],
# )
@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none(test_db):
    """Проверка получения пользователя по параметру"""
    all_users = await UserDAO.find_all(async_session=test_db)
    for num, el in enumerate(all_users):
        if el.id % 2:
            res = await UserDAO.find_one_or_none(async_session=test_db, **{"id": el.id})
        elif el.id % 5 == 0:
            res = await UserDAO.find_one_or_none(async_session=test_db, **{"first_name": el.first_name})
        elif el.id % 3 == 0:
            res = await UserDAO.find_one_or_none(async_session=test_db, **{"api_key": el.api_key})
        else:
            res = await UserDAO.find_one_or_none(async_session=test_db, **{"last_name": el.last_name})

        assert res.id == num + 1
    logger.info("ОК")


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_find_one_or_none_none(test_db):
    """Проверка получения пользователя по параметру, но вернет NONE"""
    res = await UserDAO.find_one_or_none(async_session=test_db, **{"id": 0})
    assert res is None
    logger.info("ОК")


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_add(test_db):
    """Проверка добавления пользователя и возможные ошибки"""
    test_user = UserFactory()
    add_user = await UserDAO.add(async_session=test_db, **test_user.to_dict())
    assert add_user.to_dict()["first_name"] == test_user.first_name
    with pytest.raises(SQLAlchemyError):
        await UserDAO.add(async_session=test_db, **test_user.to_dict())
        bad_user = UserFactory().to_dict()
        bad_user["api_key"] = test_user.api_key
        await UserDAO.add(async_session=test_db, **bad_user)
    del_user = await UserDAO.delete(async_session=test_db, first_name=test_user.first_name)
    assert del_user == 1
    logger.info("ОК")


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_update(test_db):
    test_user = UserFactory().to_dict()
    add_user = await UserDAO.add(async_session=test_db, **test_user)
    assert add_user.first_name == test_user["first_name"]
    test_user2 = add_user.to_dict().copy()
    test_user2["first_name"] = "new_102"
    update_user2 = await UserDAO.update(
        async_session=test_db, filter_by={"api_key": test_user["api_key"]}, **test_user2
    )
    assert update_user2[0].to_dict()["first_name"] == test_user2["first_name"]
    update_user_bad_key = await UserDAO.update(
        async_session=test_db, filter_by={"api_key": "api_key_1000"}, **test_user2
    )
    assert len(update_user_bad_key) == 0
    with pytest.raises(SQLAlchemyError):
        # Конфликт api key уникальность
        user = await UserDAO.find_one_or_none_by_id(async_session=test_db, data_id=3)
        await UserDAO.update(
            async_session=test_db, filter_by={"api_key": test_user2["id"]}, **{"api_key": user.api_key}
        )
    del_user = await UserDAO.delete(async_session=test_db, first_name=test_user2["first_name"])
    assert del_user == 1
    logger.info("ОК")


@pytest.mark.asyncio(loop_scope="session")
async def test_base_dao_delete(test_db):
    test_user = UserFactory()
    await UserDAO.add(async_session=test_db, **test_user.to_dict())
    del_user = await UserDAO.delete(async_session=test_db, first_name=test_user.first_name)
    assert del_user == 1
    logger.info("ОК")
    # del_user = await UserDAO.delete(async_session=test_db, delete_all=True)
    # assert del_user == 10
    # all_users_db = await UserDAO.find_all(async_session=test_db)
    # assert len(all_users_db) == 0
    # users = generate_users(10)
    # follows = generate_follow(10)
    # add_users = [await UserDAO.add(async_session=test_db, **user.to_dict()) for user in users]
    # add_follows = [await FollowDAO.add(async_session=test_db, **follow.to_dict()) for follow in follows]
