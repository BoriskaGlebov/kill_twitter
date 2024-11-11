from pydantic import BaseModel, ConfigDict, Field


class SUserAdd(BaseModel):
    """
    Модель для добавления нового пользователя.

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        first_name (str): Имя пользователя. Должно содержать от 1 до 50 символов.
        last_name (str): Фамилия пользователя. Должна содержать от 1 до 50 символов.
        api_key (str): Токен доступа для аутентификации пользователя.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Уникальный идентификатор пользователя.")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя пользователя, от 1 до 50 символов.")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия пользователя, от 1 до 50 символов.")
    api_key: str = Field(..., description="Токен доступа для аутентификации пользователя.")
