from datetime import datetime


def filter_by_state(operations: list[dict], state: str = 'EXECUTED') -> list[dict]:
    """Функция создает новый список по значению ключа 'state'"""
    new_operations = []
    for operation in operations:
        if operation['state'] == state:
            new_operations.append(operation)
    return new_operations


def sort_by_date(operations: list[dict], reverse: bool = True) -> list[dict]:
    """Функция сортирует списокок по дате"""
    def get_date(operation: dict) -> datetime:
        """Функция преобразует строку даты в объект datetime"""
        return datetime.strptime(operation['date'], '%Y-%m-%dT%H:%M:%S.%f')
    # Сортируем список по дате с учетом параметра reverse
    return sorted(operations, key=get_date, reverse=reverse)
