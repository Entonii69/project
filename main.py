# from src.generators import filter_by_currency, transaction_descriptions
# from src.widget import get_date, mask_account_card
#
# account_card = input(str("Введите номер счета или карты "))
#
# print(mask_account_card(account_card))
#
# user_date = input(str("Введите дату "))
#
# print(get_date(user_date))
#
# transactions = (
#     [
#         {
#             "id": 939719570,
#             "state": "EXECUTED",
#             "date": "2018-06-30T02:08:58.425572",
#             "operationAmount": {
#                 "amount": "9824.07",
#                 "currency": {
#                     "name": "USD",
#                     "code": "USD"
#                 }
#             },
#             "description": "Перевод организации",
#             "from": "Счет 75106830613657916952",
#             "to": "Счет 11776614605963066702"
#         },
#         {
#             "id": 142264268,
#             "state": "EXECUTED",
#             "date": "2019-04-04T23:20:05.206878",
#             "operationAmount": {
#                 "amount": "79114.93",
#                 "currency": {
#                     "name": "USD",
#                     "code": "USD"
#                 }
#             },
#             "description": "Перевод со счета на счет",
#             "from": "Счет 19708645243227258542",
#             "to": "Счет 75651667383060284188"
#         },
#         {
#             "id": 873106923,
#             "state": "EXECUTED",
#             "date": "2019-03-23T01:09:46.296404",
#             "operationAmount": {
#                 "amount": "43318.34",
#                 "currency": {
#                     "name": "руб.",
#                     "code": "RUB"
#                 }
#             },
#             "description": "Перевод со счета на счет",
#             "from": "Счет 44812258784861134719",
#             "to": "Счет 74489636417521191160"
#         },
#         {
#             "id": 895315941,
#             "state": "EXECUTED",
#             "date": "2018-08-19T04:27:37.904916",
#             "operationAmount": {
#                 "amount": "56883.54",
#                 "currency": {
#                     "name": "USD",
#                     "code": "USD"
#                 }
#             },
#             "description": "Перевод с карты на карту",
#             "from": "Visa Classic 6831982476737658",
#             "to": "Visa Platinum 8990922113665229"
#         },
#         {
#             "id": 594226727,
#             "state": "CANCELED",
#             "date": "2018-09-12T21:27:25.241689",
#             "operationAmount": {
#                 "amount": "67314.70",
#                 "currency": {
#                     "name": "руб.",
#                     "code": "RUB"
#                 }
#             },
#             "description": "Перевод организации",
#             "from": "Visa Platinum 1246377376343588",
#             "to": "Счет 14211924144426031657"
#         }
#     ]
# )
#
# descriptions = transaction_descriptions(transactions)
# for _ in range(5):
#     print(next(descriptions))
#
# usd_transactions = filter_by_currency(transactions, "YAN")
# for _ in range(5):
#     print(next(usd_transactions))


from src.bank_utils import process_bank_search
from src.utils import load_financial_transactions, file_path
from src.CSV_Excel_file_reader import read_csv_operations, read_excel_operations, csv_path,excel_path
from src.widget import get_date, mask_account_card


def filter_by_status(data: list, status: str) -> list:
    """Фильтрует операции по статусу (регистронезависимо)."""
    status_upper = status.strip().upper()
    valid_statuses = {'EXECUTED', 'CANCELED', 'PENDING'}
    if status_upper not in valid_statuses:
        print(valid_statuses, status_upper)
        return []
    return [
        item for item in data
        if isinstance(item, dict) and
           isinstance(item.get('state', ''), (str, int, float)) and
           str(item.get('state', '')).upper() == status_upper
    ]


def sort_data(data: list, ascending: bool = True) -> list:
    """Сортирует операции по дате (поле 'date')."""
    return sorted(data, key=lambda x: x.get('date', ''), reverse=not ascending)


def filter_ruble_transactions(data: list) -> list:
    """Оставляет только рублёвые транзакции (сумма содержит 'руб.' или 'RUB')."""
    ruble_keywords = ['руб.', 'RUB']
    result = []
    for item in data:
        if "operationAmount" in item:
            code = item.get('operationAmount', {}).get('currency', {}).get('code', '')
        elif "currency_code" in item:
            code = item.get("currency_code")
        else:
            continue
        if any(kw in str(code) for kw in ruble_keywords):
            result.append(item)
    return result


def search_keys_partial(data, substring):
    substring_lower = substring.lower()
    result = []
    for item in data:
        if not isinstance(item, dict):
            continue
        # Проверяем, есть ли ключ с подстрокой
        if any(substring_lower in key.lower() for key in item.keys()):
            result.append(item)
    return result


def format_transaction(item: dict) -> str:
    """Форматирует одну операцию для вывода."""
    date = item.get('date', 'Не указана')
    desc = item.get('description', 'Нет описания')
    if "operationAmount" in item:
        amount = item.get('operationAmount', {}).get('amount', 'Не указана')
    elif "amount" in item:
        amount = item.get('amount', 'Не указана')
    if "operationAmount" in item:
        name = item.get('operationAmount', {}).get('currency', {}).get('name', 'Не указана')
    elif "currency_name" in item:
        name = item.get('currency_name', 'Не указана')
    if item.get('from') != None:
        operation = f"{mask_account_card(item.get('from'))} -> {mask_account_card(item.get('to'))}"
    else:
        operation = f"{mask_account_card(item.get('to'))}"
    return f"{get_date(date)} {desc}\n{operation}\nСумма: {amount} {name}"


def main():
    print("Привет! Добро пожаловать в программу работы с банковскими транзакциями.")
    print("Выберите необходимый пункт меню:")
    print("1. Получить информацию о транзакциях из JSON‑файла")
    print("2. Получить информацию о транзакциях из CSV‑файла")
    print("3. Получить информацию о транзакциях из XLSX‑файла")


    choice = input("Ваш выбор (1/2/3): ").strip()


    if choice == '1':
        #filepath = r"D:\shcool\pythonProject1\data\operations.json"
        data = load_financial_transactions(file_path)
        file_type = "JSON"
    elif choice == '2':
        #filepath = r"D:\shcool\pythonProject1\data\transactions.csv"
        data = read_csv_operations(csv_path)
        file_type = "CSV"
    elif choice == '3':
        #filepath = r"D:\shcool\pythonProject1\data\transactions_excel.xlsx"
        data = read_excel_operations(excel_path)
        file_type = "XLSX"
    else:
        print("Неверный выбор. Завершаем работу.")
        return

    if not data:
        print("Данные не загружены. Завершаем работу.")
        return

    print(f"\nДля обработки выбран {file_type}-файл.")
    print(f"\nЗагружено {len(data)} операций.")

    # Фильтрация по статусу
    print("\nВведите статус, по которому необходимо выполнить фильтрацию.")
    print("Доступные для фильтровки статусы: EXECUTED, CANCELED, PENDING")
    while True:
        status = input("Статус: ").strip()
        filtered_data = filter_by_status(data, status)
        if filtered_data:
            print(f'Операции отфильтрованы по статусу "{status.upper()}"')
            break
        else:
            print(f'Статус операции "{status}" недоступен.')

    # Сортировка по дате
    print("\nОтсортировать операции по дате? Да/Нет")
    if input().strip().lower() in ['да', 'yes']:
        print("Отсортировать по возрастанию или по убыванию?")
        order = input().strip().lower()
        ascending = order in ['возрастанию', 'asc', 'по возрастанию', 'да', 'yes']
        filtered_data = sort_data(filtered_data, ascending)

    # Фильтрация рублёвых транзакций
    print("\nВыводить только рублёвые транзакции? Да/Нет")
    if input().strip().lower() in ['да', 'yes']:
        filtered_data = filter_ruble_transactions(filtered_data)


    # Поиск по описанию
    print("\nОтфильтровать список транзакций по определённому слову в описании? Да/Нет")
    if input().strip().lower() in ['да', 'yes']:
        search_word = input("Введите слово для поиска: ").strip()
        if search_word:
            filtered_data = process_bank_search(filtered_data, search_word)
    print(f"{filtered_data}")


    # Вывод результата
    print("\nРаспечатываю итоговый список транзакций...")
    if filtered_data:
        print(f"\nВсего банковских операций в выборке: {len(filtered_data)}\n")
        for i, op in enumerate(filtered_data, 1):
            print(f"{i}. {format_transaction(op)}")
            if i < len(filtered_data):
                print()  # разделитель между операциями
    else:
        print("Не найдено ни одной транзакции, подходящей под ваши условия фильтрации")

if __name__ == '__main__':
    main()
