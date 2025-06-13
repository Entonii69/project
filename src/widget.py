from datetime import datetime
from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_card: str) -> str:
    """Функция которая обрабатывает номер карты и счета"""
    if account_card.lower()[:4] == "счет":  # Проверяем, ввели номер счета или карты
        # Маскируем номер счета
        account = account_card[5:]
        mask_account = "Счет " + get_mask_account(account)
        return mask_account
    else:
        # Маскируем номер карты
        number_card = account_card[-16:]
        mask_card = account_card[:-16] + get_mask_card_number(number_card)
        return mask_card


def get_date(user_data: str) -> str:
    """Функция которая меняет формат даты"""
    if user_data == "":
        raise "Отсутствует дата"
    date = datetime.strptime(user_data, "%Y-%m-%dT%H:%M:%S.%f")
    return date.strftime("%d.%m.%Y")
