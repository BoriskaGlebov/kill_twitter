from app.dao.base import BaseDAO
from app.medias.models import Media


class MediaDAO(BaseDAO):
    model = Media
