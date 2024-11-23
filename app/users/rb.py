from typing import List, Optional

from pydantic import BaseModel, Field


class RBUsersAdd(BaseModel):
    """
    Модель для добавления нового пользователя.

    Attributes:
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        api_key (str): Не хэшированный токен при регистрации.
    """

    first_name: str = Field(..., description="Имя пользователя.")
    last_name: str = Field(..., description="Фамилия пользователя.")
    api_key: str = Field(..., description="Не хэшированный токен при регистрации.")


class RBUsersUpdate(BaseModel):
    """
    Модель для обновления информации о пользователе.

    Attributes:
        first_name (Optional[str]): Новое имя пользователя или None.
        last_name (Optional[str]): Новая фамилия пользователя или None.
        api_key (Optional[str]): Новый токен доступа или None.
    """

    first_name: Optional[str] = Field(None, description="Новое имя пользователя.")
    last_name: Optional[str] = Field(None, description="Новая фамилия пользователя.")
    api_key: Optional[str] = Field(None, description="Новый токен доступа.")


class RBCorrect(BaseModel):
    """
    Модель для успешного результата операции.

    Attributes:
        result (bool): Результат операции, всегда True.
    """

    result: bool = True


class RBUncorrect(BaseModel):
    """
    Модель для неуспешного результата операции.

    Attributes:
        result (bool): Результат операции, всегда False.
    """

    result: bool = False


class RBFollower(BaseModel):
    """
    Модель для представления подписчика.

    Attributes:
        id (int): Уникальный идентификатор подписчика.
        first_name (str): Имя подписчика.
        last_name (str): Фамилия подписчика.
    """

    id: int
    first_name: str
    last_name: str


class RBFollowing(BaseModel):
    """
    Модель для представления человека, на которого подписан пользователь.

    Attributes:
        id (int): Уникальный идентификатор человека, на которого подписан пользователь.
        first_name (str): Имя человека.
        last_name (str): Фамилия человека.
    """

    id: int
    first_name: str
    last_name: str


class RBUser(BaseModel):
    """
    Модель для представления пользователя.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        first_name (str): Имя пользователя.
        last_name (str): Фамилия пользователя.
        followers (List[RBFollower]): Список подписчиков пользователя.
        following (List[RBFollowing]): Список людей, на которых подписан пользователь.
    """

    id: int
    first_name: str
    last_name: str
    followers: List[RBFollower]
    following: List[RBFollowing]


class RBMe(BaseModel):
    """
    Модель для ответа на запрос информации о текущем пользователе.

    Attributes:
        result (bool): Результат запроса, True или False.
        user (RBUser): Информация о текущем пользователе.
    """

    result: bool
    user: RBUser
