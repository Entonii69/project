from typing import Dict, Iterator, List


def filter_by_currency(transactions: List[Dict], currency_code: str) -> Iterator[Dict]:
    """Функция принимает на вход список словарей, представляющих транзакции.
    Возвращает итератор, который поочередно выдает транзакции,
    где валюта операции соответствует заданной."""
    for transaction in transactions:
        if transaction.get('operationAmount', {}).get('currency', {}).get('code') == currency_code:
            yield transaction


def transaction_descriptions(transactions: List[Dict]) -> Iterator[str]:
    """Генератор, который принимает список словарей с транзакциями
     и возвращает описание каждой операции по очереди."""
    for transaction in transactions:
        yield transaction.get("description", "Описание отсутствует")


def card_number_generator(start: int, stop: int):
    """Генератор, который выдает номера банковских карт
    в формате XXXX XXXX XXXX XXXX, где X — цифра номера карты. """
    for number in range(start, stop + 1):
        # Форматируем число: 16 знаков, заполнение нулями
        number_str = f"{number:016d}"
        # Разбиваем на группы по 4 цифры
        formatted_card = f"{number_str[:4]} {number_str[4:8]} {number_str[8:12]} {number_str[12:]}"
        yield formatted_card


if __name__ == "__card_number_generator__":
    card_number_generator(
        start=1,
        stop=9999999999999999
    )
