import os.path
import shutil
import uuid

from fastapi import APIRouter, Depends, File, UploadFile

from app.config import settings
from app.dependencies import get_session, verify_api_key
from app.medias.dao import MediaDAO
from app.medias.models import Media
from app.medias.rb import RBMedia

router = APIRouter(prefix="/api", tags=["medias"])


@router.post("/medias", status_code=201, summary="добавить медиа")
async def upload_image(
    file: UploadFile = File(...), async_session_dep=Depends(get_session), api_key: str = Depends(verify_api_key)
) -> RBMedia:
    """
    Загрузка изображения на сервер.

    :param file: Загружаемый файл изображения. Обязательный параметр.
    :param async_session_dep: Зависимость для получения асинхронной сессии базы данных.
    :param api_key: API ключ для проверки доступа. Обязательный параметр.
    :return: Ответ с уникальным идентификатором загруженного медиафайла.
    :raises: Вызывается при ошибках в процессе загрузки или сохранения файла.
    """

    new_file_name = f"{uuid.uuid4()}_{os.path.splitext(file.filename)[0]}.jpg"
    file_location = os.path.join(settings.UPLOAD_DIRECTORY, new_file_name)
    file_save_path = os.path.join(settings.static_path(), "images", new_file_name)
    with open(file_save_path, "wb") as file_object:
        shutil.copyfileobj(file.file, file_object)
    res: Media = await MediaDAO.add(async_session=async_session_dep, **{"media_data": file_location})
    if res:
        return RBMedia(media_id=res.id)
