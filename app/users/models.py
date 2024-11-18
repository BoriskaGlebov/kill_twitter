from sqlalchemy import ForeignKey
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, int_pk, str_uniq
from app.tweets.models import Tweet


class Follow(Base):
    """
    Модель таблицы с подписчиками и подписками.

    Attributes:
        user_id (Mapped[int]): ID пользователя, который подписан.
        follower_id (Mapped[int]): ID подписчика.
        user (Mapped[List['User']]): Связь с моделью User по user_id.
        follower (Mapped[List['User']]): Связь с моделью User по follower_id.
    """

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True)
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, primary_key=True
    )

    user: Mapped[list["User"]] = relationship("User", foreign_keys=[user_id], back_populates="following", lazy="joined")
    follower: Mapped[list["User"]] = relationship(
        "User", foreign_keys=[follower_id], back_populates="followers", lazy="joined"
    )

    def __str__(self) -> str:
        """Возвращает строковое представление объекта Follow."""
        return f"{self.__class__.__name__}( " f"Пользователь={self.user_id!r}, " f"Подписан на ={self.follower_id!r})"


class User(Base):
    """
    Модель таблицы с пользователями.

    Attributes:
        id (Mapped[int_pk]): Уникальный идентификатор пользователя.
        first_name (Mapped[str]): Имя пользователя.
        last_name (Mapped[str]): Фамилия пользователя.
        api_key (Mapped[str_uniq]): Уникальный ключ API для пользователя.
        followers (Mapped[List[Follow]]): Связь с моделью Follow для подписчиков.
        followers_users (association_proxy): Упрощенный доступ к пользователям, которые подписаны на данного пользователя.
        following_users (association_proxy): Упрощенный доступ к пользователям, на которых подписан данный пользователь.
        following (Mapped[List[Follow]]): Связь с моделью Follow для пользователей, на которых подписан данный пользователь.
        tweets (Mapped[List['Tweet']]): Связь с моделью Tweet для твитов пользователя.
    """

    id: Mapped[int_pk]
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    api_key: Mapped[str_uniq]

    # Кто подписан на меня
    followers: Mapped[list[Follow]] = relationship(
        "Follow", foreign_keys="Follow.follower_id", back_populates="follower"
    )

    # Association Proxy для упрощенного доступа к подпискам
    # те на кого он подписан
    followers_users = association_proxy("followers", "user")
    # те кто подписаны на него
    following_users = association_proxy("following", "follower")

    # Связь с подписчиками кто подписан на пользователя
    # На кого подписан я
    following: Mapped[list[Follow]] = relationship("Follow", foreign_keys="Follow.user_id", back_populates="user")

    tweets: Mapped[list["Tweet"]] = relationship("Tweet", back_populates="user")

    def __str__(self):
        """Возвращает строковое представление объекта User."""
        return (
            f"{self.__class__.__name__}(id={self.id}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"api_key={self.api_key!r})"
        )
