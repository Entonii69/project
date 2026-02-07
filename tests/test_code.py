
import json
import unittest
from unittest.mock import MagicMock, mock_open, patch

import os
from typing import Any, Dict, List


import pytest
import requests


from src.external_api import convert_to_rubles

from src.decorators import log

from src.generators import card_number_generator, filter_by_currency, transaction_descriptions
from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.utils import load_financial_transactions
from src.widget import get_date, mask_account_card


def test_get_mask_card_number(fixture_get_mask_card_number: str) -> None:
    # Проверка корректной маскировки 16-значного номера
    assert get_mask_card_number(fixture_get_mask_card_number) == "4276 38** **** 9432"


@pytest.mark.parametrize(
    "incorrect_data",
    ["123456789012345", "12345678901234567", "", "123456789012345!"],
    ids=["too short", "too long", "empty string", "extraneous symbol"]
)
def test_get_mask_incorrect_card_number(incorrect_data: str) -> None:
    # Проверка обработки некорректных входных данных
    with pytest.raises(ValueError):
        get_mask_card_number(incorrect_data)


def test_get_mask_account_assert(fixture_get_mask_account: str) -> None:
    # Проверка корректной маскировки номера счета
    assert get_mask_account(fixture_get_mask_account) == "**7890"


@pytest.mark.parametrize(
    "incorrect_account",
    ["1234567890123456789", "123456789012345678901", "", "1@34j67890123456789!"],
    ids=["too short", "too long", "empty string", "extraneous symbol"]
)
def test_get_mask_account(incorrect_account: str) -> None:
    # Проверка обработки некорректных входных данных
    with pytest.raises(ValueError):
        get_mask_account(incorrect_account)


@pytest.mark.parametrize(
    "input_data, output_data",
    [
        ("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
        ("Счет 64686473678894779589", "Счет **9589"),
        ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
        ("Счет 35383033474447895560", "Счет **5560"),
        ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
        ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
        ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
        ("Счет 73654108430135874305", "Счет **4305")
    ]
)
def test_mask_account_card_assert(input_data: str, output_data: str) -> None:
    # Проверка универсальности функции
    assert mask_account_card(input_data) == output_data


def test_mask_account_card_incorrect() -> None:
    # Проверка обработки некорректных входных данных
    with pytest.raises(Exception):
        mask_account_card("")  # Пустая строка


def test_get_date_assert(fixture_get_date: str) -> None:
    # Проверка правильности определения даты
    assert get_date(fixture_get_date) == "11.03.2024"


@pytest.mark.parametrize(
    "incorrect_date",
    ["2025-05-14T02:26:18", ""],
    ids=["too short", "empty string"]
)
def test_get_date_incorrect(incorrect_date: str) -> None:
    # Проверка обработки некорректных входных данных
    with pytest.raises(Exception):
        get_date(incorrect_date)  # Неверный формат даты


@pytest.mark.parametrize(
    "test_list, test_state, test_result",
    [
        (
            [
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
            ], 'CANCELED',
            [
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
            ]
        ),
        (
            [
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
            ], 'EXECUTED',
            [
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}
            ]
        )
    ]
)
def test_filter_by_state(
    test_list: List[Dict[str, Any]],
    test_state: str,
    test_result: List[Dict[str, Any]]
) -> None:
    # Проверка сортировки списка словарей
    assert filter_by_state(test_list, test_state) == test_result


@pytest.mark.parametrize(
    "test_list_date, test_reverse, test_result_reverse_date, test_result_date",
    [
        (
            [
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}
            ], False,
            [
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}
            ],
            [
                {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
                {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}
            ]
        )
    ]
)
def test_sort_by_date(
    test_list_date: List[Dict[str, Any]],
    test_reverse: bool,
    test_result_reverse_date: List[Dict[str, Any]],
    test_result_date: List[Dict[str, Any]]
) -> None:
    assert sort_by_date(test_list_date, test_reverse) == test_result_reverse_date
    assert sort_by_date(test_list_date) == test_result_date


# Тест filter_by_currency
def test_filter_by_currency(fixture_get_transactions: List[Dict[str, Any]]) -> None:
    # Проверяем USD
    usd_iter = filter_by_currency(fixture_get_transactions, "USD")
    assert next(usd_iter)["id"] == 939719570

    # Проверяем, что больше нет элементов
    with pytest.raises(StopIteration):
        next(usd_iter)


def test_filter_by_currency_incorrect() -> None:
    transactions = [
        {
            "id": 939719570,
            "state": "EXECUTED",
            "date": "2018-06-30T02:08:58.425572",
            "operationAmount": {
                "amount": "9824.07",
                "currency": {"name": "USD", "code": "USD"}
            },
            "description": "Перевод организации",
            "from": "Счет 75106830613657916952",
            "to": "Счет 11776614605963066702"
        },
        {
            "id": 142264268,
            "state": "EXECUTED",
            "date": "2019-04-04T23:20:05.206878",
            "operationAmount": {
                "amount": "79114.93",
                "currency": {"name": "руб.", "code": "RUB"}
            },
            "description": "Перевод со счета на счет",
            "from": "Счет 19708645243227258542",
            "to": "Счет 75651667383060284188"
        }
    ]
    # Фильтруем по валюте, которой нет в списке
    result = list(filter_by_currency(transactions, "YUN"))
    # Правильное ожидание - пустой список
    expected: List[Dict[str, Any]] = []
    assert result == expected


def test_filter_by_currency_empty(fixture_get_transactions: List[Dict[str, Any]]) -> None:
    # Проверяем валюту, которой нет
    eur_iter = filter_by_currency(fixture_get_transactions, "EUR")
    # Превращаем в список и проверяем, что он пустой
    assert list(eur_iter) == []


# Тест transaction_descriptions
def test_transaction_descriptions(fixture_get_transactions: List[Dict[str, Any]]) -> None:
    descriptions = list(transaction_descriptions(fixture_get_transactions))
    assert descriptions == ["Перевод организации", "Перевод со счета на счет"]


# Тест card_number_generator
@pytest.mark.parametrize("start, stop, expected", [
    (1, 1, ["0000 0000 0000 0001"]),
    (10, 12, ["0000 0000 0000 0010", "0000 0000 0000 0011", "0000 0000 0000 0012"]),
])
def test_card_number_generator(start: int, stop: int, expected: List[str]) -> None:
    assert list(card_number_generator(start, stop)) == expected


# Тестовые функции для проверки
@log()
def test_function_success(x: int, y: int) -> int:
    return x + y


@log()
def test_function_error(x: int, y: int) -> float:
    return x / y


# Тест с логированием в файл
@log(filename="test.log")
def test_function_file(x: int, y: int) -> int:
    return x + y


# Тестовые случаи
def test_success_console(capsys) -> None:
    # Проверяем успешный вызов функции с логированием в консоль
    result = test_function_success(1, 2)
    captured = capsys.readouterr()

    assert result == 3
    assert "Starting test_function_success" in captured.out
    assert "test_function_success ok" in captured.out


def test_error_console(capsys) -> None:
    # Проверяем обработку ошибки с логированием в консоль
    with pytest.raises(TypeError):
        test_function_success("a", 2)

    captured = capsys.readouterr()
    assert "Starting test_function_success" in captured.out
    assert "test_function_success error: unsupported operand type(s) for +: 'str' and 'int'" in captured.out
    assert "Inputs: ('a', 2), {}" in captured.out


def test_success_file() -> None:
    # Проверяем успешный вызов функции с логированием в файл
    result = test_function_file(3, 4)

    assert result == 7

    # Проверяем содержимое файла
    with open("test.log", "r") as f:
        content = f.read()
        assert "Starting test_function_file" in content
        assert "test_function_file ok" in content

    # Удаляем тестовый файл после проверки
    os.remove("test.log")


def test_error_file() -> None:
    # Проверяем обработку ошибки с логированием в файл
    with pytest.raises(ZeroDivisionError):
        test_function_error(1, 0)

    # Проверяем содержимое файла
    with open("test.log", "r") as f:
        content = f.read()
        assert "Starting test_function_error" in content
        assert "test_function_error error: division by zero" in content
        assert "Inputs: (1, 0), {}" in content

    # Удаляем тестовый файл после проверки
    os.remove("test.log")


def test_no_args() -> None:
    # Проверяем работу декоратора без аргументов
    @log()
    def no_args_func() -> str:
        return "test"

    result = no_args_func()
    assert result == "test"


def test_empty_args() -> None:
    # Проверяем работу с пустыми аргументами
    @log()
    def empty_args_func() -> str:
        return "test"

    result = empty_args_func()
    assert result == "test"
