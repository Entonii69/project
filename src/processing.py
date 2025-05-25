from datetime import datetime

operations = [
    {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
    {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
    {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
    {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
]


def filter_by_state(operations: list[dict], state: str = 'EXECUTED') -> list[dict]:
    """Функция создает новый список по значению ключа 'state'"""
    new_operations = []
    for operation in operations:
        for value_state in operation.values():
            if value_state == 'EXECUTED':
                new_operations.append(operation)
    return new_operations


def sort_by_date(operations: list[dict], reverse: bool = True) -> list[dict]:
    """Функция сортирует списокок по дате"""
    def get_date(operation: dict) -> datetime:
        """Функция преобразует строку даты в объект datetime"""
        return datetime.strptime(operation['date'], '%Y-%m-%dT%H:%M:%S.%f')
    # Сортируем список по дате с учетом параметра reverse
    return sorted(operations, key=get_date, reverse=reverse)
