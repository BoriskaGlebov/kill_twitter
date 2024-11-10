from app.config import get_settings


def test_config(config):
    """Проверка правлиьности насроек для работы приложения локально"""
    assert config.get_test_db_url() == "postgresql+asyncpg://admin:password@localhost:5432/test_kill_twitter"
    assert config.get_db_url() == "postgresql+asyncpg://admin:password@localhost:5432/kill_twitter"


def test_monkeypass(monkeypatch):
    """Проверка правлиьности насроек для работы приложения в контейнере"""
    monkeypatch.setenv("ENV", "docker")
    config = get_settings()
    assert config.get_test_db_url() == "postgresql+asyncpg://admin:password@db:5432/test_kill_twitter"
    assert config.get_db_url() == "postgresql+asyncpg://admin:password@db:5432/kill_twitter"
