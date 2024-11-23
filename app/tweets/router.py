from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session, verify_api_key
from app.tweets.dao import LikeDAO, TweetDAO, TweetMediaDAO
from app.tweets.models import Like, Tweet
from app.tweets.rb import RBCorrect, RBTweet, RBUncorrect
from app.tweets.schemas import STweet
from app.users.dao import UserDAO
from app.users.models import User

router = APIRouter(prefix="/api", tags=["tweets"])


@router.post("/tweets", summary="Добавить твит", response_model=RBTweet)
async def add_tweet(
    tweet_data: STweet, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBTweet:
    """
    Добавляет новый твит.

    :param tweet_data: Данные твита.
    :type tweet_data: STweet
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: API ключ для аутентификации пользователя.
    :type api_key: str
    :return: Результат операции с идентификатором нового твита.
    :rtype: RBTweet
    """
    user_id: User = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})
    tweet_dict = tweet_data.model_dump()
    tweet_dict["user_id"] = user_id.id
    media_ids = []
    if not tweet_dict["tweet_media_ids"]:
        del tweet_dict["tweet_media_ids"]
    else:
        media_ids.extend(tweet_dict["tweet_media_ids"])
        del tweet_dict["tweet_media_ids"]
    add_new_tweet: Tweet = await TweetDAO.add(async_session=async_session_dep, **tweet_dict)
    if media_ids:
        for id in media_ids:
            await TweetMediaDAO.add(async_session=async_session_dep, **{"tweet_id": add_new_tweet.id, "media_id": id})
    out: RBTweet = RBTweet(tweet_id=add_new_tweet.id)
    return out


@router.delete("/tweets/{id}", summary="Удалить твит", response_model=RBCorrect | RBUncorrect)
async def delete_tweet(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBCorrect | RBUncorrect:
    """
    Удаляет твит по его идентификатору.

    :param id: Идентификатор твита для удаления.
    :type id: int
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: API ключ для аутентификации пользователя.
    :type api_key: str
    :return: Результат операции удаления.
    :rtype: RBCorrect | RBUncorrect
    """
    tweet = await TweetDAO.delete(async_session=async_session_dep, **{"id": id})
    if tweet:
        return RBCorrect()
    else:
        return RBUncorrect()


@router.post("/tweets/{id}/likes", summary="Поставить лайк на твит", response_model=RBCorrect | RBUncorrect)
async def like_tweet(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBCorrect | RBUncorrect:
    """
    Ставит лайк на твит.

    :param id: Идентификатор твита для лайка.
    :type id: int
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: API ключ для аутентификации пользователя.
    :type api_key: str
    :return: Результат операции лайка.
    :rtype: RBCorrect | RBUncorrect
    """
    user_id: User = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})

    tweet: Like = await LikeDAO.add(
        async_session=async_session_dep, **{"user_id": user_id.id, "tweet_id": id, "like": True}
    )
    if tweet:
        return RBCorrect()
    else:
        return RBUncorrect()


@router.delete("/tweets/{id}/likes", summary="Удалить лайк на твит", response_model=RBCorrect | RBUncorrect)
async def rollback_like_tweet(
    id: int, async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBCorrect | RBUncorrect:
    """
    Удаляет лайк с твита.

    :param id: Идентификатор твита для удаления лайка.
    :type id: int
    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: API ключ для аутентификации пользователя.
    :type api_key: str
    :return: Результат операции удаления лайка.
    :rtype: RBCorrect | RBUncorrect
    """
    user_id: User = await UserDAO.find_one_or_none(async_session=async_session_dep, **{"api_key": api_key})

    tweet: int = await LikeDAO.delete(async_session=async_session_dep, **{"user_id": user_id.id, "tweet_id": id})
    if tweet:
        return RBCorrect()
    else:
        return RBUncorrect()


@router.get("/tweets", summary="Получить ленту с твитами")
async def get_user_tweets(
    async_session_dep: AsyncSession = Depends(get_session), api_key: str = Depends(verify_api_key)
) -> dict:
    """
    Получает ленту твитов.

    :param async_session_dep: Асинхронная сессия базы данных.
    :param api_key: API ключ для аутентификации пользователя.
    :type api_key: str
    :return: Словарь с результатом и списком твитов.
    :rtype: dict
    """
    out = {"result": True, "tweets": []}
    tweets = await TweetDAO.find_all(async_session=async_session_dep)
    ra = sorted(tweets, key=lambda o: len(o.likes), reverse=True)
    # print(user)
    for tweet in ra:
        tweet_info = {
            "id": tweet.id,
            "content": tweet.tweet_data,
            "attachments": [el.media_data for el in tweet.tweets_media],
            "author": {"id": tweet.user.id, "name": tweet.user.first_name},
            "likes": [],
        }

        for like in tweet.likes:
            likes_info = {
                "user_id": like.user_id,
                "name": (
                    await UserDAO.find_one_or_none(async_session=async_session_dep, **{"id": like.user_id})
                ).first_name,
            }
            tweet_info["likes"].append(likes_info)
        out["tweets"].append(tweet_info)
    return out
