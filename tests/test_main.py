import os.path

from sqlalchemy import select

from models.model import ListRecipes, Recipes


async def test_start(db_session):
    res = os.path.exists("test_recipes.db")
    # async with db_client as session:
    qr_rec = await db_session.execute(select(Recipes))
    res_recipes = qr_rec.scalars().all()
    #
    qr_list_rec = await db_session.execute(select(ListRecipes))
    res_list_rec = qr_list_rec.scalars().all()
    assert res
    assert len(res_recipes) == 10
    assert len(res_list_rec) == 10


async def test_add_recipes(db_session):
    test_recipe = Recipes(
        name="Test_recipes",
        ingredients={"Интгридиент1": "10 шт", "Интгридиент2": "11 шт", "Интгридиент3": "13 шт"},
        description="Тестовое сообщение",
        some_inf=ListRecipes(),
    )
    db_session.add(test_recipe)
    await db_session.commit()
    qr_rec = (await db_session.execute(select(Recipes))).scalars().all()
    qr_list_rec = (await db_session.execute(select(ListRecipes))).scalars().all()
    assert len(qr_rec) == 11
    assert len(qr_list_rec) == 11


#
async def test_hello_world(api_client):
    response = api_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"hello": "world"}


# #
async def test_get_recipes_id(api_client, db_session):
    response = api_client.get("/recipes/1")
    # print(response.json())
    assert response.status_code == 200
    assert response.json()["id"] == 1


#
async def test_add_recipes_api(api_client, db_session):
    data = {
        "some_recipe": {"name": "еуые", "ingredients": {"тестовый ингридиент": "1 шт"}, "description": "string"},
        "some_list_recipe": {"cooking_time": "1150 минут"},
    }
    response = api_client.post("/recipes", json=data)
    async with db_session as session:
        q = await session.execute(select(Recipes))
        result = q.scalars().all()
        len_res = len(result)
    assert response.status_code == 200
    assert response.json()["id"] == result[len_res - 1].id


#
