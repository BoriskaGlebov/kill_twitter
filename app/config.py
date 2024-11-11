import os

from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

env_file_local: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
env_file_docker: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.docker")


class Settings(BaseSettings):
    """
    Схема с конфигурацией приложения

    """

    DB_USER: str
    DB_PASSWORD: SecretStr
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_TEST: str
    UPLOAD_DIRECTORY: str
    PYTHONPATH: str

    model_config = SettingsConfigDict(extra="ignore")

    def get_db_url(self) -> str:
        """
        Получает url для Боевой БД
        :return: url
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_test_db_url(self) -> str:
        """
        Получает url для Тестовой БД
        :return: url
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_TEST}"
        )

    @classmethod
    def static_path(cls) -> str:
        """Путь к директории для статических файлов"""
        return os.path.join(os.path.dirname(__file__), "static")

    @classmethod
    def template_path(cls) -> str:
        """Путь к директории для файлов html"""
        return os.path.join(os.path.dirname(__file__), "templates")


def get_settings() -> Settings:
    """Получение базовых настроек приложения"""
    env_file = env_file_docker if os.getenv("ENV") == "docker" else env_file_local
    try:
        print(env_file)
        return Settings(_env_file=env_file)
    except ValidationError as e:
        # Извлечение сообщений об ошибках с указанием полей
        error_messages = []
        for error in e.errors():
            field = error["loc"]  # Получаем местоположение ошибки
            message = error["msg"]  # Получаем сообщение об ошибке
            error_messages.append(f"Field '{field[-1]}' error: {message}")  # Указываем поле и сообщение

        raise RuntimeError(f"Validation errors: {', '.join(error_messages)}")


try:
    settings = get_settings()
    print(settings)
except RuntimeError as e:
    print(e)
