from pydantic import BaseModel, ConfigDict, Field


class STweet(BaseModel):
    """
    Модель для представления твита.

    :param tweet_data: Текст твита.
    :param tweet_media_ids: Список идентификаторов медиафайлов, связанных с твитом.
    """

    model_config = ConfigDict(from_attributes=True)
    tweet_data: str = Field(..., description="Текст Твита")
    tweet_media_ids: list[int] | None = Field(None, description="Список медиа файлов их id")
