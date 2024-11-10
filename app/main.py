from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.params import Depends
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.database import Base, async_engine, async_session
from models.model import ListRecipes, Recipes, start_data
from models.utilits.schemas import ListRecipesModel, RecipesIn, RecipesOut

app = FastAPI()


async def get_session() -> AsyncGenerator:
    """Функция необходима для тестирования, теперь на тестах
    обращеие происходит к тестовой БД, а работа в Боевой БД"""
    async with async_session() as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print("Application is starting up...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    rec_list = start_data()
    async with async_session() as session:
        session.add_all(rec_list)
        await session.commit()
        # print(rec_list)
        yield  # Control returns here after startup logic
    # Code to run on shutdown
    print("Application is shutting down...")
    await async_engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def hello():
    return {"hello": "world"}


@app.get("/recipes/{id}", response_model=RecipesOut)
async def get_recipes_id(id: int, session_dep=Depends(get_session)) -> Recipes:
    async with session_dep as session:
        qr = await session.execute(select(Recipes).where(Recipes.id == id).options(selectinload(Recipes.some_inf)))
        res = qr.scalars().one_or_none()
        # print(res)
        if res:
            res.some_inf.views += 1
            # print(res.some_inf)
            await session.commit()
            return res
        else:
            raise HTTPException(status_code=404, detail="Item not found")


@app.post("/recipes", response_model=RecipesOut)
async def add_recipes(some_recipe: RecipesIn, some_list_recipe: ListRecipesModel, session_dep=Depends(get_session)):
    new_list = ListRecipes(**some_list_recipe.model_dump())
    new_recipe = Recipes(**some_recipe.model_dump())
    new_recipe.some_inf = new_list
    async with session_dep as session:
        session.add(new_recipe)
        await session.commit()

        return new_recipe


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
