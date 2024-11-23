from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, int_pk
from app.users.models import User


class Tweet(Base):
    """
    Модель таблицы с твитами.

    Attributes:
        id (Mapped[int_pk]): Уникальный идентификатор твита.
        user_id (Mapped[int]): Идентификатор пользователя, который создал твит.
        tweet_data (Mapped[str]): Текст твита.
        user (Mapped[User]): Связь с моделью User, представляющая пользователя, который создал твит.
        likes (Mapped[list[Like]]): Связь с моделью Like, представляющая лайки на этот твит.
        tweets_media (Mapped[list[Media]]): Связь с моделью Media для хранения медиафайлов, связанных с твитом.
    """

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tweet_data: Mapped[str]
    user: Mapped["User"] = relationship("User", back_populates="tweets")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user_like", lazy="joined")
    tweets_media = relationship("Media", secondary="tweetmedias", back_populates="tweets", lazy="joined")

    def __str__(self):
        return f"{self.__class__.__name__}( " f"пользователь={self.user_id!r}, " f"Твит ={self.tweet_data!r})"


class TweetMedia(Base):
    """
    Модель для реализации отношения многие ко многим между таблицами с медиафайлами и твитами.

    Attributes:
        tweet_id (Mapped[int]): Идентификатор твита.
        media_id (Mapped[int]): Идентификатор медиафайла.
    """

    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey("medias.id", ondelete="CASCADE"), primary_key=True)


class Like(Base):
    """
    Модель для представления лайков на твиты конкретным пользователем.

    Attributes:
        user_id (Mapped[int]): Идентификатор пользователя, который поставил лайк.
        tweet_id (Mapped[int]): Идентификатор твита, на который поставлен лайк.
        like (Mapped[bool]): Флаг, указывающий на наличие лайка (по умолчанию True).
        user_like (Mapped[Tweet]): Связь с моделью Tweet для получения информации о твите.
    """

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True)
    like: Mapped[bool] = mapped_column(Boolean, default=True)
    user_like: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")
