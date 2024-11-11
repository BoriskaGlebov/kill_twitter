from typing import Any, Dict, Optional, Sequence, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO
from app.users.models import Follow, User


class UserDAO(BaseDAO[User]):
    model: Type[User] = User

    @classmethod
    async def user_info(
        cls,
        async_session: AsyncSession,
        api_key: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Получаю подписчиков и подписки в удобном формате.

        :param async_session: Асинхронная сессия.
        :param api_key: Ключ доступа.
        :param user_id: ID пользователя.
        :return: Информация о пользователе и его подписках.
        """
        async with async_session as session:
            out: Dict[str, Any] = {"result": True}
            out_keys = ("id", "first_name", "last_name")
            query = select(cls.model).options(
                selectinload(cls.model.followers),
                selectinload(cls.model.following),
            )
            result = await session.execute(query)
            all_users: Sequence[User] = result.scalars().all()

            for user in all_users:
                if user.api_key == api_key or user.id == user_id:
                    out["user"] = {k: v for k, v in user.to_dict().items() if k in out_keys}
                    out["user"]["followers"] = [
                        {k: v for k, v in user_f.to_dict().items() if k in out_keys} for user_f in user.followers_users
                    ]
                    out["user"]["following"] = [
                        {k: v for k, v in user_f.to_dict().items() if k in out_keys} for user_f in user.following_users
                    ]
                    break

            if out.get("user"):
                return out
            else:
                out["result"] = False
                return out

    # @classmethod
    # async def get_all_tweets(cls, async_session: async_sessionmaker[AsyncSession], api_key: str) -> Optional[User]:
    #     """
    #     Получить все твиты пользователя по API ключу.
    #
    #     :param async_session: Асинхронная сессия.
    #     :param api_key: Ключ доступа.
    #     :return: Информация о пользователе или None.
    #     """
    #     async with async_session() as session:
    #         query = select(cls.model).options(selectinload(cls.model.tweets)).filter_by(api_key=api_key)
    #         result = await session.execute(query)
    #         user_inf: Optional[User] = result.unique().scalars().one_or_none()
    #         return user_inf


class FollowDAO(BaseDAO[Follow]):
    model: type[Follow] = Follow  # Добавьте типизацию для модели Follow
