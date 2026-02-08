import json
import unittest
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest
import requests
from pandas.errors import EmptyDataError, ParserError

from src.CSV_Excel_file_reader import read_csv_operations, read_excel_operations
from src.external_api import convert_to_rubles
from src.generators import card_number_generator, filter_by_currency, transaction_descriptions
from src.masks import get_mask_account, get_mask_card_number
from src.processing import filter_by_state, sort_by_date
from src.utils import load_financial_transactions
from src.widget import get_date, mask_account_card


def test_get_mask_card_number(fixture_get_mask_card_number):
    # Проверка корректной маскировки 16-значного номера
    assert get_mask_card_number(fixture_get_mask_card_number) == "4276 38** **** 9432"


@pytest.mark.parametrize(
    "incorrect_data",
    ["123456789012345", "12345678901234567", "", "123456789012345!"],
    ids=["too short", "too long", "empty string", "extraneous symbol"]
)
def test_get_mask_incorrect_card_number(incorrect_data):
    # Проверка обработки некорректных входных данных
    with pytest.raises(ValueError):
        get_mask_card_number(incorrect_data)


def test_get_mask_account_assert(fixture_get_mask_account):
    # Проверка корректной маскировки номера счета
    assert get_mask_account(fixture_get_mask_account) == "**7890"


@pytest.mark.parametrize(
    "incorrect_account",
    ["1234567890123456789", "123456789012345678901", "", "1@34j67890123456789!"],
    ids=["too short", "too long", "empty string", "extraneous symbol"]
)
def test_get_mask_account(incorrect_account):
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
def test_mask_account_card_assert(input_data, output_data):
    # Проверка универсальности функции
    assert mask_account_card(input_data) == output_data


def test_mask_account_card_incorrect() -> None:
    # Проверка обработки некорректных входных данных
    with pytest.raises(Exception):
        mask_account_card("")  # Пустая строка


def test_get_date_assert(fixture_get_date):
    # Проверка правильности определения даты
    assert get_date(fixture_get_date) == "11.03.2024"


@pytest.mark.parametrize(
    "incorrect_date",
    ["2025-05-14T02:26:18", ""],
    ids=["too short", "empty string"]
)
def test_get_date_incorrect(incorrect_date):
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
def test_filter_by_state(test_list, test_state, test_result):
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
def test_sort_by_date(test_list_date, test_reverse, test_result_reverse_date, test_result_date):
    assert sort_by_date(test_list_date, test_reverse) == test_result_reverse_date
    assert sort_by_date(test_list_date) == test_result_date


# Тест filter_by_currency
def test_filter_by_currency(fixture_get_transactions):
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
    expected = []
    assert result == expected


def test_filter_by_currency_empty(fixture_get_transactions):
    # Проверяем валюту, которой нет
    eur_iter = filter_by_currency(fixture_get_transactions, "EUR")
    # Превращаем в список и проверяем, что он пустой
    assert list(eur_iter) == []


# Тест transaction_descriptions
def test_transaction_descriptions(fixture_get_transactions):
    descriptions = list(transaction_descriptions(fixture_get_transactions))
    assert descriptions == ["Перевод организации", "Перевод со счета на счет"]


# Тест card_number_generator
@pytest.mark.parametrize("start, stop, expected", [
    (1, 1, ["0000 0000 0000 0001"]),
    (10, 12, ["0000 0000 0000 0010", "0000 0000 0000 0011", "0000 0000 0000 0012"]),
])
def test_card_number_generator(start, stop, expected):
    assert list(card_number_generator(start, stop)) == expected


class TestConvertToRubles(unittest.TestCase):

    def setUp(self):
        """Подготовка общих данных для тестов"""
        self.valid_transaction = {
            "operationAmount": {
                "amount": 100.0,
                "currency": {"code": "USD"}
            }
        }
        self.rub_transaction = {
            "operationAmount": {
                "amount": 500.0,
                "currency": {"code": "RUB"}
            }
        }
        self.invalid_currency_transaction = {
            "operationAmount": {
                "amount": 100.0,
                "currency": {"code": "JPY"}  # не в CURRENCY
            }
        }

    @patch("requests.get")
    def test_rub_currency_returns_amount(self, mock_get):
        """Если валюта — RUB, возвращается исходная сумма без запроса к API"""
        result = convert_to_rubles(self.rub_transaction)
        self.assertEqual(result, 500.0)
        mock_get.assert_not_called()  # запрос к API не выполнялся

    @patch("requests.get")
    def test_valid_currency_success_response(self, mock_get):
        """Успешная конвертация для валюты из CURRENCY (USD → RUB)"""
        # Настраиваем мок: успешный ответ API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": 9500.0}
        mock_get.return_value = mock_response

        result = convert_to_rubles(self.valid_transaction)

        # Проверяем результат
        self.assertEqual(result, 9500.0)

        # Проверяем, что запрос был сделан с правильными параметрами
        expected_url = "https://api.apilayer.com/exchangerates_data/convert?to=RUB&from=USD&amount=100.0"
        mock_get.assert_called_with(
            expected_url,
            headers={"apikey": unittest.mock.ANY}  # API_KEY может быть None в тестах
        )

    @patch("requests.get")
    def test_api_returns_error_status(self, mock_get):
        """Если API возвращает статус != 200, функция возвращает 0.0"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response

        result = convert_to_rubles(self.valid_transaction)

        self.assertEqual(result, 0.0)
        # Можно дополнительно проверить, что было напечатано сообщение (через capsys в pytest)

    @patch("requests.get")
    def test_request_exception_handled(self, mock_get):
        """Если возникает исключение при запросе (например, нет сети), функция возвращает  0.0"""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        result = convert_to_rubles(self.valid_transaction)

        self.assertEqual(result, 0.0)

    def test_currency_not_in_currency_list(self):
        """Если валюта не в CURRENCY, функция возвращает 0.0 без запроса к API"""
        with patch("requests.get") as mock_get:
            result = convert_to_rubles(self.invalid_currency_transaction)
            self.assertEqual(result, 0.0)
            mock_get.assert_not_called()

    def test_missing_operation_amount(self):
        """Если нет 'operationAmount', функция возвращает 0.0"""
        transaction = {}
        result = convert_to_rubles(transaction)
        self.assertEqual(result, 0.0)

    def test_missing_amount_in_operation(self):
        """Если в 'operationAmount' нет 'amount', возвращается 0.0"""
        transaction = {
            "operationAmount": {
                "currency": {"code": "USD"}
            }
        }
        result = convert_to_rubles(transaction)
        self.assertEqual(result, 0.0)

    def test_missing_currency_code(self):
        """Если в 'currency' нет 'code', возвращается 0.0"""
        transaction = {
            "operationAmount": {
                "amount": 100.0,
                "currency": {}  # нет 'code'
            }
        }
        result = convert_to_rubles(transaction)
        self.assertEqual(result, 0.0)

    @patch("requests.get")
    def test_empty_response_json(self, mock_get):
        """Если ответ API — пустой JSON, функция возвращает 0.0"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}  # пустой ответ
        mock_get.return_value = mock_response

        result = convert_to_rubles(self.valid_transaction)

        self.assertEqual(result, 0.0)

    @patch("requests.get")
    def test_response_without_result_key(self, mock_get):
        """Если в ответе API нет ключа 'result', функция возвращает 0.0"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"some_key": "value"}  # нет 'result'
        mock_get.return_value = mock_response

        result = convert_to_rubles(self.valid_transaction)

        self.assertEqual(result, 0.0)


class TestLoadFinancialTransactions(unittest.TestCase):

    def setUp(self):
        self.valid_json_content = [
            {"id": 1, "amount": 100.0, "currency": "USD"},
            {"id": 2, "amount": 200.0, "currency": "EUR"}
        ]
        self.invalid_json_content = "{invalid json}"  # ← строка, не JSON
        self.file_path = "test_transactions.json"

    @patch("os.path.exists")
    def test_file_not_exists(self, mock_exists):
        mock_exists.return_value = False
        result = load_financial_transactions(self.file_path)
        self.assertEqual(result, [])
        mock_exists.assert_called_with(self.file_path)

    @patch("os.path.exists", return_value=True)
    def test_valid_json_file(self, mock_exists):
        """Если файл существует и содержит валидный JSON‑список, возвращается этот список"""
        # Создаём мок для open с валидным JSON
        mock_file = mock_open(read_data=json.dumps(self.valid_json_content))
        with patch("builtins.open", mock_file):
            result = load_financial_transactions(self.file_path)

        self.assertEqual(result, self.valid_json_content)
        mock_file.assert_called_once_with(self.file_path, 'r', encoding='utf-8')

    @patch("os.path.exists", return_value=True)
    def test_invalid_json_file(self, mock_exists):
        """Если файл содержит невалидный JSON, возвращается пустой список"""
        # Создаём мок для open с невалидным JSON
        mock_file = mock_open(read_data=self.invalid_json_content)

        # Мокируем json.load, чтобы он выбрасывал исключение
        with patch("builtins.open", mock_file), \
                patch("json.load", side_effect=json.JSONDecodeError("Expecting value", "", 0)):
            result = load_financial_transactions(self.file_path)

        self.assertEqual(result, [])
        mock_file.assert_called_once_with(self.file_path, 'r', encoding='utf-8')

    @patch("os.path.exists", return_value=True)
    def test_io_error_on_open(self, mock_exists):
        """Если при открытии файла возникает IOError, возвращается пустой список"""
        with patch("builtins.open", side_effect=IOError("Permission denied")):
            result = load_financial_transactions(self.file_path)

        self.assertEqual(result, [])

    @patch("os.path.exists", return_value=True)
    def test_json_not_a_list(self, mock_exists):
        """Если JSON — не список (например, словарь), возвращается пустой список"""
        mock_file = mock_open(read_data='{"key": "value"}')
        with patch("builtins.open", mock_file):
            result = load_financial_transactions(self.file_path)

        self.assertEqual(result, [])
        mock_file.assert_called_once_with(self.file_path, 'r', encoding='utf-8')

    @patch("os.path.exists", return_value=True)
    def test_empty_json_list(self, mock_exists):
        """Если JSON — пустой список, возвращается пустой список"""
        mock_file = mock_open(read_data='[]')
        with patch("builtins.open", mock_file):
            result = load_financial_transactions(self.file_path)

        self.assertEqual(result, [])
        mock_file.assert_called_once_with(self.file_path, 'r', encoding='utf-8')


class TestFinancialOperationsWithMock(unittest.TestCase):

    @patch('os.path.exists')
    def test_csv_file_not_found(self, mock_exists):
        """Тест: файл CSV не существует."""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            read_csv_operations("nonexistent.csv")

        self.assertIn("Файл не найден", str(context.exception))

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_csv')
    def test_csv_empty_file(self, mock_read_csv, mock_exists):
        """Тест: CSV-файл пуст."""
        mock_read_csv.return_value = pd.DataFrame()  # пустой DataFrame

        with self.assertRaises(EmptyDataError) as context:
            read_csv_operations("empty.csv")

        self.assertEqual(str(context.exception), "Файл пуст.")

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_csv', side_effect=ParserError("Malformed CSV"))
    def test_csv_parser_error(self, mock_read_csv, mock_exists):
        """Тест: ошибка парсинга CSV."""
        with self.assertRaises(ParserError) as context:
            read_csv_operations("bad.csv")

        self.assertIn("Ошибка парсинга CSV", str(context.exception))

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_csv', side_effect=Exception("Unknown error"))
    def test_csv_unexpected_error(self, mock_read_csv, mock_exists):
        """Тест: неожиданная ошибка при чтении CSV."""
        with self.assertRaises(Exception) as context:
            read_csv_operations("error.csv")

        self.assertIn("Неожиданная ошибка при чтении CSV", str(context.exception))

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_csv')
    def test_csv_success(self, mock_read_csv, mock_exists):
        """Тест: успешное чтение CSV."""
        # Подменяем результат read_csv
        mock_df = pd.DataFrame({
            'date': ['2023-10-01'],
            'amount': [1000],
            'category': ['Salary'],
            'description': ['Зарплата']
        })
        mock_read_csv.return_value = mock_df

        result = read_csv_operations("valid.csv")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['amount'], 1000)
        self.assertEqual(result[0]['category'], 'Salary')

    # --- Тесты для Excel ---

    @patch('os.path.exists')
    def test_excel_file_not_found(self, mock_exists):
        """Тест: файл Excel не существует."""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError) as context:
            read_excel_operations("nonexistent.xlsx")

        self.assertIn("Файл не найден", str(context.exception))

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_excel')
    def test_excel_empty_file(self, mock_read_excel, mock_exists):
        """Тест: Excel-файл пуст."""
        mock_read_excel.return_value = pd.DataFrame()  # пустой DataFrame

        with self.assertRaises(ValueError) as context:
            read_excel_operations("empty.xlsx")

        self.assertEqual(str(context.exception), "Файл Excel пуст.")

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_excel', side_effect=ValueError("No sheet"))
    def test_excel_no_sheet(self, mock_read_excel, mock_exists):
        """Тест: в Excel нет листов."""
        with self.assertRaises(ValueError) as context:
            read_excel_operations("no_sheet.xlsx")

        self.assertEqual(str(context.exception), "В файле Excel нет листов.")

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_excel', side_effect=Exception("Unknown Excel error"))
    def test_excel_unexpected_error(self, mock_read_excel, mock_exists):
        """Тест: неожиданная ошибка при чтении Excel."""
        with self.assertRaises(Exception) as context:
            read_excel_operations("error.xlsx")

        self.assertIn("Неожиданная ошибка при чтении Excel", str(context.exception))

    @patch('os.path.exists', return_value=True)
    @patch('pandas.read_excel')
    def test_excel_success(self, mock_read_excel, mock_exists):
        """Тест: успешное чтение Excel."""
        # Подменяем результат read_excel
        mock_df = pd.DataFrame({
            'date': ['2023-10-01'],
            'amount': [1000],
            'category': ['Salary'],
            'description': ['Зарплата']
        })
        mock_read_excel.return_value = mock_df

        result = read_excel_operations("valid.xlsx")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['amount'], 1000)
        self.assertEqual(result[0]['category'], 'Salary')
