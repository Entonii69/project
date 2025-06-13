from src.processing import filter_by_state, sort_by_date
from src.widget import get_date, mask_account_card

account_card = input(str("Введите номер счета или карты "))

print(mask_account_card(account_card))

user_date = input(str("Введите дату "))
