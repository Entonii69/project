import functools
import logging
from typing import Any, Callable


def log(filename: str = None) -> Decorator:
    """Декоратор, который будет автоматически логировать начало и конец выполнения функции,
    а также ее результаты или возникшие ошибки. Декоратор принимает необязательный аргумент
    filename, который определяет, куда будут записываться логи."""
    # Настраиваем базовую конфигурацию логирования
    logger = logging.getLogger('function_logger')
    logger.setLevel(logging.INFO)

    # Формируем обработчики в зависимости от filename
    if filename:
        handler = logging.FileHandler(filename)
    else:
        handler = logging.StreamHandler()

    # Устанавливаем простой формат вывода
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                # Записываем начало выполнения
                logger.info(f"Starting {func.__name__}")

                # Выполняем функцию
                result = func(*args, **kwargs)

                # Логируем успешный результат
                logger.info(f"{func.__name__} ok")
                return result
            except Exception as e:
                # Формируем сообщение об ошибке
                error_message = (
                    f"{func.__name__} error: {str(e)}. "
                    f"Inputs: {args}, {kwargs}"
                )
                logger.error(error_message)
                raise  # Перебрасываем исключение

        return wrapper

    return decorator
