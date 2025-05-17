from src.masks import get_mask_account, get_mask_card_number


def mask_account_card(account_card: str) -> str:
    """Функция которая обрабатывает номер карты и счета"""
    if account_card[:4] == "Счет":
        account = account_card[5:]
        mask_account = account_card[:5] + get_mask_account(account)
        return mask_account
    else:
        number_card = account_card[-16:]
        mask_card = account_card[:-16] + get_mask_card_number(number_card)
        return mask_card

