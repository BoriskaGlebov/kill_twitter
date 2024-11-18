from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, engine, int_pk
from app.users.models import User


class Tweet(Base):
    """
    Модель таблицы с твитами
    """

    id: Mapped[int_pk]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    tweet_data: Mapped[str]
    # tweet_media_ids: Mapped[int] = mapped_column(Integer, nullable=True)
    # tweets_media: Mapped[list['TweetMedia']] = relationship('TweetMedia', back_populates='tweet')
    user: Mapped["User"] = relationship("User", back_populates="tweets")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="user_like", lazy="joined")
    tweets_media = relationship("Media", secondary="tweetmedias", back_populates="tweets", lazy="joined")

    def __str__(self):
        return f"{self.__class__.__name__}( " f"пользователь={self.user_id!r}, " f"Твит ={self.tweet_data!r})"


class TweetMedia(Base):
    """
    Моедли реализует отношение многие ко многим у таблиц с картинками и с тивитами
    """

    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True)
    media_id: Mapped[int] = mapped_column(ForeignKey("medias.id", ondelete="CASCADE"), primary_key=True)
    # tweet: Mapped[list['Tweet']] = relationship("Tweet", back_populates='tweets_media')
    # media: Mapped[list['Media']] = relationship("Media", back_populates='medias')


class Like(Base):
    """ЛАйки на твит конкретнвым пользователем"""

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"), primary_key=True)
    like: Mapped[bool] = mapped_column(Boolean, default=True)
    user_like: Mapped["Tweet"] = relationship("Tweet", back_populates="likes")


if __name__ == "__main__":
    Base.metadata.create_all(engine)
