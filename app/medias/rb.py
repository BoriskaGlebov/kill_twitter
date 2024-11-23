from pydantic import BaseModel


class RBMedia(BaseModel):
    """
    Модель для представления медиафайла в ответе API.

    Attributes:
        result (bool): Статус выполнения операции (по умолчанию True).
        media_id (int): Уникальный идентификатор медиафайла.
    """

    result: bool = True
    media_id: int
