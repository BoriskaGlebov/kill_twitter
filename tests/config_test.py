import os
from unittest.mock import patch

import pytest

from app.config import get_settings, logger


def test_config(config):
    """Проверка правильности настроек для работы приложения локально"""
    assert config.get_test_db_url() == "postgresql+asyncpg://admin:password@localhost:5432/test_kill_twitter"
    assert config.get_db_url() == "postgresql+asyncpg://admin:password@localhost:5432/kill_twitter"
    logger.info("ОК")


def test_monkeypass(monkeypatch):
    """Проверка правильности настроек для работы приложения в контейнере"""
    monkeypatch.setenv("ENV", "docker")
    config = get_settings()
    assert config.get_test_db_url() == "postgresql+asyncpg://admin:password@db:5432/test_kill_twitter"
    assert config.get_db_url() == "postgresql+asyncpg://admin:password@db:5432/kill_twitter"
    logger.info("ОК")


# Тест на некорректные значения в .env
def test_invalid_settings():
    """# Тест на некорректные значения в .env"""
    with patch.dict(
        os.environ,
        {
            "DB_USER": "",
            "DB_PASSWORD": "",  # Пустой SecretStr
            "DB_HOST": "localhost",
            "DB_PORT": "invalid_port",  # Некорректный порт (должен быть int)
            "DB_NAME": "test_db",
            "DB_TEST": "test_db_test",
            "UPLOAD_DIRECTORY": "/uploads",
            "PYTHONPATH": "/app",
        },
    ):
        with pytest.raises(RuntimeError):
            get_settings()  # Вызов функции для получения настроек
    logger.info("ОК")
