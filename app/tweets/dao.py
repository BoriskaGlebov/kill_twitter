from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.dao.base import BaseDAO
from app.tweets.models import Like, Tweet, TweetMedia


class TweetDAO(BaseDAO):
    model = Tweet

    @classmethod
    async def find_all(cls, async_session, **filter_by):
        async with async_session as session:
            query = select(cls.model).options(
                selectinload(cls.model.user), selectinload(cls.model.likes), selectinload(cls.model.tweets_media)
            )
            res = await session.execute(query)
            tweets = res.unique().scalars().all()
            return tweets


class TweetMediaDAO(BaseDAO):
    model = TweetMedia


class LikeDAO(BaseDAO):
    model = Like
