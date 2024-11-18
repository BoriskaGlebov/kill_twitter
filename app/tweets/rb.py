from pydantic import BaseModel


class RBTweet(BaseModel):
    result: bool = True
    tweet_id: int


# class RBUsersAdd(BaseModel):
#     first_name: str = Field(..., description="Имя")
#     last_name: str = Field(..., description="Фамилия")
#     api_key: str = Field(..., description="Token при регистрации не хэшированный")
#
#
# class RBUsersUpdate(BaseModel):
#     first_name: str | None = None
#     last_name: str | None = None
#     api_key: str | None = None
#
#
class RBCorrect(BaseModel):
    result: bool = True


class RBUncorrect(BaseModel):
    result: bool = False


#
#
# class RBFollower(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#
# class RBFollowing(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#
# class RBUser(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#     followers: List[RBFollower]
#     following: List[RBFollowing]
#
# class RBMe(BaseModel):
#     result: bool
#     user: RBUser
