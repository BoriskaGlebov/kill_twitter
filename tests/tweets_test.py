import pytest

from app.config import logger
from app.data_generate import TweetFactory


@pytest.mark.asyncio(loop_scope="session")
async def test_add_tweet(async_client, test_db):
    """Тест добавить твит."""
    tweet = TweetFactory()
    # Некоррректный твит
    res1 = await async_client.post("/api/tweets", json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]})
    assert res1.status_code == 403
    assert res1.json()["error_message"] == "Не указан токен в заголовке"
    res2 = await async_client.post(
        "/api/tweets", headers={"api-key": "tes"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]}
    )
    assert res2.status_code == 403
    assert res2.json()["error_message"] == "Такого токена не существует, введите корректный токен"
    # Корректный запрос
    res3 = await async_client.post(
        "/api/tweets", headers={"api-key": "test"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]}
    )
    assert res3.status_code == 201
    assert res3.json()["result"] is True

    res4 = await async_client.post(
        "/api/tweets", headers={"api-key": "test"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": []}
    )
    assert res4.status_code == 201
    assert res4.json()["result"] is True
    await async_client.delete(f"/tweets/{res3.json()['tweet_id']}")
    await async_client.delete(f"/tweets/{res4.json()['tweet_id']}")
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_tweet(async_client, test_db):
    """Тест удаление твита."""
    tweet = TweetFactory()
    # Некоррректный твит
    res1 = await async_client.delete("/api/tweets/1")
    assert res1.status_code == 403
    assert res1.json()["error_message"] == "Не указан токен в заголовке"
    res2 = await async_client.delete("/api/tweets/1", headers={"api-key": "tes"})
    assert res2.status_code == 403
    assert res2.json()["error_message"] == "Такого токена не существует, введите корректный токен"
    # # Корректный запрос
    res3 = await async_client.post(
        "/api/tweets", headers={"api-key": "test"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]}
    )
    assert res3.status_code == 201
    assert res3.json()["result"] is True
    res4 = await async_client.delete(f"/api/tweets/{res3.json()['tweet_id']}", headers={"api-key": "test"})
    assert res4.status_code == 200
    assert res4.json()["result"] is True
    res5 = await async_client.delete("/api/tweets/10000", headers={"api-key": "test"})
    assert res5.status_code == 200
    assert res5.json()["result"] is False
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_like_tweet(async_client, test_db):
    """Тест поставить лайк твиту."""
    tweet = TweetFactory()
    new_tweet = await async_client.post(
        "/api/tweets", headers={"api-key": "test"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]}
    )
    # Проверка некорректных запросов
    res1 = await async_client.post("/api/tweets/1/likes")
    assert res1.status_code == 403
    assert res1.json()["error_message"] == "Не указан токен в заголовке"
    res2 = await async_client.post("/api/tweets/1/likes", headers={"api-key": "te"})
    assert res2.status_code == 403
    assert res2.json()["error_message"] == "Такого токена не существует, введите корректный токен"
    # Корректные запрос
    res3 = await async_client.post(f"/api/tweets/{new_tweet.json()['tweet_id']}/likes", headers={"api-key": "test"})
    assert res3.status_code == 200
    assert res3.json()["result"] is True
    res4 = await async_client.post("/api/tweets/10000/likes", headers={"api-key": "test"})
    assert res4.status_code == 409
    assert res4.json()["result"] is False
    await async_client.delete(f"/tweets/{tweet.id}")
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_rollback_like_tweet(async_client, test_db):
    """Тест поставить лайк твиту."""
    tweet = TweetFactory()
    new_tweet = await async_client.post(
        "/api/tweets", headers={"api-key": "test"}, json={"tweet_data": tweet.tweet_data, "tweet_media_ids": [1, 2]}
    )
    await async_client.post(f"/api/tweets/{new_tweet.json()['tweet_id']}/likes", headers={"api-key": "test"})
    # Проверка некорректных запросов
    res1 = await async_client.delete("/api/tweets/1/likes")
    assert res1.status_code == 403
    assert res1.json()["error_message"] == "Не указан токен в заголовке"
    res2 = await async_client.delete("/api/tweets/1/likes", headers={"api-key": "te"})
    assert res2.status_code == 403
    assert res2.json()["error_message"] == "Такого токена не существует, введите корректный токен"
    # Корректные запрос
    res3 = await async_client.delete(f"/api/tweets/{new_tweet.json()['tweet_id']}/likes", headers={"api-key": "test"})
    assert res3.status_code == 200
    assert res3.json()["result"] is True
    res4 = await async_client.delete("/api/tweets/10000/likes", headers={"api-key": "test"})
    assert res4.status_code == 200
    assert res4.json()["result"] is False
    logger.info("OK")


@pytest.mark.asyncio(loop_scope="session")
async def test_get_user_tweets(async_client, test_db):
    """Тест поставить лайк твиту."""
    # некорректные запросы
    res1 = await async_client.get("/api/tweets")
    assert res1.status_code == 403
    assert res1.json()["error_message"] == "Не указан токен в заголовке"
    res2 = await async_client.get("/api/tweets", headers={"api-key": "te"})
    assert res2.status_code == 403
    assert res2.json()["error_message"] == "Такого токена не существует, введите корректный токен"
    # Корректные запрос
    res3 = await async_client.get("/api/tweets", headers={"api-key": "test"})
    assert res3.status_code == 200
    assert res3.json()["result"] is True
    logger.info("OK")
