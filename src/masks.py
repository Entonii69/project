def get_mask_card_number(number_card: str) -> str:
    """Функция которая маскирует номера карты"""
    mask_number_card = number_card[:4] + " " + number_card[4:6] + "** **** " + number_card[-4:]
    return mask_number_card


def get_mask_account(account: str) -> str:
    """Функция которая маскирует номер счета"""
    mask_account = "**" + account[-4:]
    return mask_account
