import pytest

from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card


def test_get_mask_card_number(fixture_get_mask_card_number):
    # Проверка корректной маскировки 16-значного номера
    assert get_mask_card_number(fixture_get_mask_card_number) == "4276 38** **** 9432"

    # Проверка обработки некорректных входных данных
    with pytest.raises(ValueError):
        get_mask_card_number("123456789012345")  # Меньше 16 цифр
    with pytest.raises(ValueError):
        get_mask_card_number("12345678901234567")  # Больше 16 цифр
    with pytest.raises(ValueError):
        get_mask_card_number("")  # Пустая строка

    # Проверка с нечисловыми символами
    with pytest.raises(ValueError):
        get_mask_card_number("abcd123456789012")  # Буквы в начале
    with pytest.raises(ValueError):
        get_mask_card_number("123456789012abcd")  # Буквы в конце
    with pytest.raises(ValueError):
        get_mask_card_number("1234-5678-9012-3")  # Символы дефиса


def test_get_mask_account(fixture_get_mask_account):
    # Проверка корректной маскировки номера счета
    assert get_mask_account(fixture_get_mask_account) == "**7890"

    # Проверка обработки некорректных входных данных
    with pytest.raises(ValueError):
        get_mask_account("1234567890123456789")  # Меньше 20 цифр
    with pytest.raises(ValueError):
        get_mask_account("123456789012345678901")  # Больше 20 цифра
    with pytest.raises(ValueError):
        get_mask_account("")  # Пустая строка

    # Проверка с нечисловыми символами
    with pytest.raises(ValueError):
        get_mask_account("abcd5678901234567890")
    with pytest.raises(ValueError):
        get_mask_account("1234!/.8901234567890")


@pytest.mark.parametrize("input_data, output_data",
                         [("Maestro 1596837868705199", "Maestro 1596 83** **** 5199"),
                          ("Счет 64686473678894779589", "Счет **9589"),
                          ("MasterCard 7158300734726758", "MasterCard 7158 30** **** 6758"),
                          ("Счет 35383033474447895560", "Счет **5560"),
                          ("Visa Classic 6831982476737658", "Visa Classic 6831 98** **** 7658"),
                          ("Visa Platinum 8990922113665229", "Visa Platinum 8990 92** **** 5229"),
                          ("Visa Gold 5999414228426353", "Visa Gold 5999 41** **** 6353"),
                          ("Счет 73654108430135874305", "Счет **4305")])
def test_mask_account_card(input_data, output_data):
    # Проверка правильность определения счета
    assert mask_account_card("Счет 12345678901234567890") == "Счет **7890"

    # Проверка правильность определения карты
    assert mask_account_card("Visa Platinum 7000792289606361") == "Visa Platinum 7000 79** **** 6361"
    assert mask_account_card("Visa Classic 6831982476737658") == "Visa Classic 6831 98** **** 7658"
    assert mask_account_card("Maestro 1596837868705199") == "Maestro 1596 83** **** 5199"
    assert mask_account_card("MasterCard 7158300734726758") == "MasterCard 7158 30** **** 6758"

    # Проверка универсальности функции
    assert mask_account_card(input_data) == output_data

    # Проверка обработки некорректных входных данных
    with pytest.raises(Exception):
        mask_account_card("")  # Пустая строка


def test_get_date(fixture_get_date):
    # Проверка правильности определения даты
    assert get_date(fixture_get_date) == "11.03.2024"

    # Проверка обработки некорректных входных данных
    with pytest.raises(Exception):
        get_date("2025-05-14T02:26:18")  # Неверный формат даты
    with pytest.raises(Exception):
        get_date("")  # Пустая строка


@pytest.mark.parametrize("test_list, test_state, test_result",
                         [([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}], 'CANCELED',
                           [{'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}]),
                          ([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}], 'EXECUTED',
                           [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}])])
def test_filter_by_state(test_list, test_state, test_result):
    # Проверка сортировки списка словарей
    assert filter_by_state(test_list, test_state) == test_result


@pytest.mark.parametrize("test_list_date, test_reverse, test_result_reverse_date, test_result_date",
                         [([{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'}], False,
                           [{'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'},
                            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
                            {'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'}],
                           [{'id': 41428829, 'state': 'EXECUTED', 'date': '2019-07-03T18:35:29.512364'},
                            {'id': 615064591, 'state': 'CANCELED', 'date': '2018-10-14T08:21:33.419441'},
                            {'id': 594226727, 'state': 'CANCELED', 'date': '2018-09-12T21:27:25.241689'},
                            {'id': 939719570, 'state': 'EXECUTED', 'date': '2018-06-30T02:08:58.425572'}])])
def test_sort_by_date(test_list_date, test_reverse, test_result_reverse_date, test_result_date):
    assert sort_by_date(test_list_date, test_reverse) == test_result_reverse_date
    assert sort_by_date(test_list_date) == test_result_date
