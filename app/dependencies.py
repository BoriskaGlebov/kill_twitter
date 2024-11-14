import asyncio
from typing import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

# from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session
from app.users.dao import UserDAO

# from app.tweets.dao import TweetDAO, TweetMediaDAO
# from app.medias.dao import MediaDAO
# from app.tweets.models import Tweet, TweetMedia
# from app.medias.models import Media


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция для получения асинхронной сессии базы данных.

    Эта функция используется для тестирования и работы с базой данных.
    В тестах происходит обращение к тестовой базе данных,
    а в рабочем приложении — к боевой базе данных.

    :yield: Асинхронная сессия базы данных (AsyncSession)
    """
    async with async_session() as session:
        yield session


# API_KEY = "test"  # Замените на ваш реальный ключ
api_key_header = APIKeyHeader(name="api-key", auto_error=False)


# Зависимость для проверки API-ключа
async def verify_api_key(async_session_dep=Depends(get_session), api_key: str = Depends(api_key_header)):
    if api_key:
        res = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})
        if res:
            return api_key
        else:
            raise HTTPException(status_code=403, detail="Такого токена не существует, введите корректный токен")
    else:
        raise HTTPException(status_code=403, detail="Не указан токен в заголовке")


async def main():
    """Здесь я тестирую методы работы с БД"""
    # async for session in get_session():
    #     out = {"result": True, "tweets": []}
    #
    #     sel_user = select(User).filter_by(**{"id": 1})
    #     users = await session.execute(sel_user)
    #     res: User = users.unique().scalars().one_or_none()
    #     print(res)
    #     print("*" * 50)
    #     for el in res.tweets:
    #         tweet_info = {
    #             "id": el.id,
    #             "content": el.tweet_data,
    #             "attachments": [el.media_data for el in el.tweets_media],
    #             "author": {"id": res.id, "name": res.first_name},
    #             "likes": [],
    #         }
    #         likes_info = {"user_id": 0, "name": ""}
    #         out["tweets"].append(tweet_info)
    #     pprint(out)
    # print(el.tweets_media)
    # for path in el.tweets_media:
    #     print(path.to_dict())
    #     tweet_info['id']=

    # sel_tweet = select(Tweet.id,
    #                    Tweet.user_id,
    #                    Tweet.tweet_data,Media.id,Media.media_data).filter_by(**{'user_id': res.id}).join(TweetMedia,
    #                                                                            TweetMedia.tweet_id == Tweet.id).join(Media,Media.id==TweetMedia.media_id)
    # tweets = await session.execute(sel_tweet)
    # res_tweets = tweets.all()
    # # print(res_tweets)
    # for tweet in res_tweets:
    #     print(tweet)
    #     tw_inf = {'id': tweet.id,
    #               'content': tweet.tweet_data,
    #               'attachments': [],
    #               'author': {
    #                   'id': res.id,
    #                   'name': res.first_name
    #               }}
    #     out['tweets'].append(tw_inf)
    # pprint(out)
    # q = select(User).filter_by(id=1)
    # users = await session.execute(q)
    # res = users.unique().scalars().all()
    # for el in res:
    #     print(el)
    #     for ek in el.tweets:
    #         print(ek)
    # q=select(Tweet).filter_by(user_id=3)
    # tweets=await session.execute(q)
    # res=tweets.unique().scalars().all()
    # print(res)
    # for mes in res:
    #     print(mes)
    #     for med in mes.tweets_media:
    #         print(med.to_dict())


if __name__ == "__main__":
    asyncio.run(main())
