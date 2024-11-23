from typing import Any, Dict, Optional, Type

from sqlalchemy import Sequence, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO
from app.tweets.models import Like, Tweet, TweetMedia


class TweetDAO(BaseDAO[Tweet]):
    """
    Класс для доступа к данным в БД.

    Работает с таблицей Tweet
    """

    model: Type[Tweet] = Tweet

    @classmethod
    async def find_all(cls, async_session: AsyncSession, **filter_by: Optional[Dict[str, Any]]) -> Sequence[Tweet]:
        """
        Получить все твиты с возможностью фильтрации.

        :param async_session: Асинхронная сессия SQLAlchemy для выполнения запросов.
        :param filter_by: Дополнительные параметры фильтрации в виде именованных аргументов.
                          Например, можно передать {'user_id': 1} для фильтрации твитов конкретного пользователя.
        :return: Список объектов Tweet, соответствующих запросу.
        """
        async with async_session as session:
            query = select(cls.model).options(
                selectinload(cls.model.user), selectinload(cls.model.likes), selectinload(cls.model.tweets_media)
            )
            res = await session.execute(query)
            tweets = res.unique().scalars().all()
            return tweets


class TweetMediaDAO(BaseDAO[TweetMedia]):
    """
    Класс для доступа к данным в БД.

    Работает с таблицей TweetMedia
    """

    model: Type[TweetMedia] = TweetMedia


class LikeDAO(BaseDAO[Like]):
    """
    Класс для доступа к данным в БД.

    Работает с таблицей Like
    """

    model: Type[Like] = Like
