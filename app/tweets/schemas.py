from pydantic import BaseModel, ConfigDict, Field


class STweet(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    tweet_data: str = Field(..., description="Текст Твита")
    tweet_media_ids: list[int] = Field(None, description="Список медиа файлов их id")
