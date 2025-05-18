from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_card: str) -> str:
    """Функция которая обрабатывает номер карты и счета"""
    if account_card[:4] == "Счет": # Проверяем, ввели номер счета или карты
        # Маскируем номер счета
        account = account_card[5:]
        mask_account = account_card[:5] + get_mask_account(account)
        return mask_account
    else:
        # Маскируем номер карты
        number_card = account_card[-16:]
        mask_card = account_card[:-16] + get_mask_card_number(number_card)
        return mask_card


def get_date(user_data: str) -> str:
    """Функция которая меняет формат даты"""
    date = '"' + user_data[8:10] + "." + user_data[5:7] + "." + user_data[:4] + '"'
    return date