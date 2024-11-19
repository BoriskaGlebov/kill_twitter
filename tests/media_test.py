import os.path

import pytest

from app.config import logger
from app.data_generate import UserFactory
from app.medias.dao import MediaDAO


@pytest.mark.asyncio(loop_scope="session")
async def test_upload_image(async_client, test_db):
    """Тест добавления медиа файлов"""
    user = UserFactory()
    await async_client.post("/api/users", params=user.to_dict())
    # Не авторизован
    no_api_key = await async_client.post("/api/medias")
    assert no_api_key.status_code == 403
    assert no_api_key.json()["result"] is False
    # Без медиа
    no_media = await async_client.post("/api/medias", headers={"api-key": user.api_key})
    assert no_media.status_code == 400
    assert no_media.json()["result"] is False
    if os.path.split(os.getcwd())[1] == "tests":
        filepath = os.path.join("1.jpg")
    elif os.path.split(os.getcwd())[1] == "kill_twitter":
        filepath = os.path.join("tests", "1.jpg")
    with open(filepath, "rb") as file:
        files = {"file": ("1.jpg", file)}
        correct = await async_client.post("/api/medias", headers={"api-key": user.api_key}, files=files)
        assert correct.status_code == 201
    #
    media_name = await MediaDAO.find_one_or_none_by_id(async_session=test_db, data_id=correct.json()["media_id"])
    # file_path=media_name.to_dict()['media_data']
    if os.path.split(os.getcwd())[1] == "tests":
        file_path = os.path.join("..", "app" + media_name.to_dict()["media_data"])
    elif os.path.split(os.getcwd())[1] == "kill_twitter":
        file_path = os.path.join("app" + media_name.to_dict()["media_data"])
    os.remove(file_path)
    logger.info("OK")
