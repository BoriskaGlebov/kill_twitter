from typing import Type

from app.dao.base import BaseDAO
from app.medias.models import Media


class MediaDAO(BaseDAO[Media]):
    """
    Класс для доступа к данным в БД.

    Работает с таблицей Media
    """

    model: Type[Media] = Media
