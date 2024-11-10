from pydantic import BaseModel


class ListRecipesModel(BaseModel):
    # name: int
    # views: int
    cooking_time: str
    # recipe: Mapped['Recipes'] = relationship(back_populates="some_inf")


class ListRecipesModelOut(ListRecipesModel):
    name: int
    views: int

    class Config:
        from_attributes = True


class RecipesModel(BaseModel):
    name: str
    ingredients: dict = {"тестовый ингридиент": "1 шт"}
    description: str
    # some_inf:ListRecipesModel


class RecipesIn(RecipesModel): ...


class RecipesOut(RecipesModel):
    id: int
    some_inf: ListRecipesModelOut

    class Config:
        from_attributes = True
