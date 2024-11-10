from random import choice, randint

from sqlalchemy import Column, ForeignKey, PickleType
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.database import Base


class Recipes(Base):
    __tablename__ = "Recipes"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    # не нашел способ как записывать в БД словарь или список, в том числе хотелось бы записать через mapped_column
    ingredients = Column(PickleType, nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    some_inf: Mapped["ListRecipes"] = relationship(back_populates="recipe", cascade="all, delete-orphan")

    def __repr__(self):
        return "".join([str(getattr(self, c.name)) + " - " for c in self.__table__.columns])


class ListRecipes(Base):
    __tablename__ = "ListRecipes"
    name: Mapped[int] = mapped_column(ForeignKey("Recipes.id"), primary_key=True)
    views: Mapped[int] = mapped_column(nullable=False, default=0)
    cooking_time: Mapped[str] = mapped_column(default=f"{randint(30, 120)} минут")
    recipe: Mapped["Recipes"] = relationship(back_populates="some_inf")

    def __repr__(self):
        return "".join([str(getattr(self, c.name)) + " - " for c in self.__table__.columns])


def start_data() -> list[Recipes]:
    name = [
        "Жаркое",
        "Суп",
        "Жареная картошка",
        "Макароны",
        "Запеканка",
        "Омлет",
        "Овсяная каша с фруктами",
        "Шашлык",
        "Борщ",
        "Плов",
        "Компот",
        "Запеканка",
        "Торт",
        "Гречневая каша с тушенкой",
        "Овощной салат",
        "Перловая каша",
        "Лазанья",
        "Винегрет",
    ]
    ingredients = [
        "лук",
        "морковка",
        "макароны",
        "свинина",
        "картофель",
        "огурцы",
        "помидоры",
        "болгарский перец",
        "яблоки",
        "бананы",
        "апельсины",
        "сливочное масло",
        "соль",
        "специи",
        "чеснок",
        "сахар",
        "варенье",
        "мята",
        "свекла",
        "молоко",
        "сок",
        "кабачки",
        "тыква",
        "арахис",
        "грецкий орех",
        "изюм",
        "гречка",
        "рис",
        "овсяная крупа",
        "горох",
        "яйца",
        "кофе",
        "чай",
        "абрикос",
        "персик",
        "арбуз",
    ]
    description = [
        "все порезать посолить",
        "варить 30 минут",
        "жарить на медленном огне",
        "резать мелкими кубиками",
        "помыть",
        "добавить по вкусу",
        "запекать в духовке",
        "температура 200 градусов",
        "достать из холодильника",
        "потрясти перед применением",
        "резать полосками",
        "варить до полной готовности",
    ]
    return [
        Recipes(
            name=choice(name),
            ingredients={choice(ingredients): f"{randint(1, n + 1)} шт" for n in range(randint(1, 5))},
            description=",".join([choice(description) for _ in range(3)]),
            some_inf=ListRecipes(),
        )
        for _ in range(10)
    ]
