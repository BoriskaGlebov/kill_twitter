from pydantic import BaseModel


class RBTweet(BaseModel):
    """
    Модель для представления результата операции с твитом.

    Attributes:
        result (bool): Флаг, указывающий на успешность операции. По умолчанию True.
        tweet_id (int): Уникальный идентификатор твита.
    """

    result: bool = True
    tweet_id: int


class RBCorrect(BaseModel):
    """
    Модель для представления результата корректной операции.

    Attributes:
        result (bool): Флаг, указывающий на успешность операции. По умолчанию True.
    """

    result: bool = True


class RBUncorrect(BaseModel):
    """
    Модель для представления результата некорректной операции.

    Attributes:
        result (bool): Флаг, указывающий на успешность операции. По умолчанию False.
    """

    result: bool = False
