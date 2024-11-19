from typing import Type

from app.dao.base import BaseDAO
from app.medias.models import Media


class MediaDAO(BaseDAO[Media]):
    model: Type[Media] = Media
