from src.processing import filter_by_state, operations, sort_by_date
from src.widget import get_date, mask_account_card

account_card = input(str("Введите номер счета или карты "))

print(mask_account_card(account_card))

user_date = input(str("Введите дату "))

print(get_date(user_date))
print(filter_by_state(operations))
print(sort_by_date(operations))
