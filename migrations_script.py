import os.path
import subprocess

from app.config import logger

alembic_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
alembic_path_in_main = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
current_dir = os.path.split(os.path.dirname(__file__))


def run_alembic_command(command: str) -> None:
    """
    Запускает команду alembic.

    :param command: Команда для выполнения в виде строки.
    :raises SystemExit: Если команда завершилась с ошибкой, программа завершится с соответствующим кодом ошибки.
    """

    result: subprocess.CompletedProcess[str] = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Ошибка при выполнении команды: {' '.join(command)}")
        exit(result.returncode)
    if "test" in command:
        logger.info("Команды для Тестовой БД")
    else:
        logger.info("Команды для Основной БД")
    logger.info(f"Логи работы alembic\n{result.stderr.strip()}")
    logger.info(f"Стандартный вывод в консоль {result.stdout}\n".strip())


if __name__ == "__main__":
    # Применение миграции к основной БД
    run_alembic_command(f"alembic --config {alembic_path} upgrade head")
    run_alembic_command(f"alembic --config {alembic_path} current")

    # Применяем миграции для тестовой базы данных
    run_alembic_command(f"alembic --config {alembic_path} -x db=test upgrade head")
    run_alembic_command(f"alembic --config {alembic_path} -x db=test current")
