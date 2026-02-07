import json
import logging
import os
from typing import Dict, List

# Настройка логгера для модуля utils
# Указываем путь к файлу логов
log_utils_path = r"D:\shcool\pythonProject1\logs\utils.log"

logging.basicConfig(
    filename=log_utils_path,
    filemode='a',           # режим: 'a' (дописывать) или 'w' (перезаписывать)
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)


def load_financial_transactions(file_path: str) -> List[Dict]:
    """Загружает финансовые транзакции из JSON-файла."""
    # Логирование входа в функцию (DEBUG)
    logger.debug("Начало загрузки транзакций. Файл: %r", file_path)

    # Проверка существования файла
    if not os.path.exists(file_path):
        logger.warning("Файл не найден: %r", file_path)
        return []

    try:
        # Попытка открыть и прочитать файл
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Проверка, что данные — список
        if isinstance(data, list):
            logger.info("Успешно загружено %d транзакций из файла: %r", len(data), file_path)
            return data
        else:
            logger.warning(
                "Данные в файле не являются списком (тип: %s). Файл: %r",
                type(data).__name__, file_path
            )
            return []

    except json.JSONDecodeError as e:
        logger.error(
            "Ошибка JSON в файле %r: %s (строка %d, столбец %d)",
            file_path, e.msg, e.lineno, e.colno
        )
        return []

    except PermissionError:
        logger.error("Нет прав на чтение файла: %r", file_path)
        return []

    except FileNotFoundError:
        # Может возникнуть, если файл удалили между проверкой и открытием
        logger.error("Файл не найден при чтении: %r", file_path)
        return []

    except OSError as e:
        logger.error("OS-ошибка при работе с файлом %r: %s", file_path, e)
        return []

    except Exception as e:
        # Неожиданная ошибка (логируем с трассировкой)
        logger.critical(
            "Неожиданная ошибка при загрузке файла %r: %s",
            file_path, type(e).__name__
        )
        logger.exception(e)  # Выводит полную трассировку
        return []
