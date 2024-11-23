from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, int_pk


class Media(Base):
    """
    Модель таблицы с картинками (медиафайлами).

    Attributes:
        id (int): Уникальный идентификатор медиафайла (первичный ключ).
        media_data (str): Данные о медиафайле (например, путь к изображению или URL).
        tweets (List[Tweet]): Связь с твитами через промежуточную таблицу `tweetmedias`.
    """

    id: Mapped[int_pk]
    media_data: Mapped[str] = mapped_column(String)
    tweets = relationship("Tweet", secondary="tweetmedias", back_populates="tweets_media")
