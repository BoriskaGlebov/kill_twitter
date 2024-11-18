import os
import sys

from loguru import logger
from pydantic import SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# Удаляем все существующие обработчики
logger.remove()

# Настройка логирования
logger.add(
    sys.stdout,
    level="DEBUG",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - "
    "<level>{level:^8}</level> - "
    "<cyan>{name}</cyan>:<magenta>{line}</magenta> - "
    "<yellow>{function}</yellow> - "
    "<white>{message}</white> <magenta>{extra[user]:^10}</magenta>",
)
# Конфигурация логгера с дополнительными полями
logger.configure(extra={"ip": "", "user": ""})
logger.add(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "file.log"),
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {name}:{line} - {function} - {message} {extra[user]}",
    rotation="1 day",
    retention="7 days",
    backtrace=True,
    diagnose=True,
)

# Теперь вы можете использовать logger в других модулях
# Явный экспорт для того что б mypy не ругался
__all__ = ["logger"]

env_file_local: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
env_file_docker: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env.docker")


class Settings(BaseSettings):
    """
    Схема с конфигурацией приложения.

    Атрибуты:
        DB_USER (str): Пользователь базы данных.
        DB_PASSWORD (SecretStr): Пароль базы данных (секрет).
        DB_HOST (str): Хост базы данных.
        DB_PORT (int): Порт базы данных.
        DB_NAME (str): Имя основной базы данных.
        DB_TEST (str): Имя тестовой базы данных.
        UPLOAD_DIRECTORY (str): Директория для загрузки файлов.
        PYTHONPATH (str): Путь к Python.
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
        Получает URL для основной базы данных.

        :return: URL базы данных в формате строки.
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD.get_secret_value()}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    def get_test_db_url(self) -> str:
        """
        Получает URL для тестовой базы данных.

        :return: URL тестовой базы данных в формате строки.
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
        """Возвращает путь к директории для файлов HTML."""
        return os.path.join(os.path.dirname(__file__), "templates")


def get_settings() -> Settings:
    """Возвращает путь к директории для файлов HTML."""
    env_file = env_file_docker if os.getenv("ENV") == "docker" else env_file_local
    try:
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
except RuntimeError as e:
    print(e)
