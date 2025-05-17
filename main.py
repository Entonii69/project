from src.widget import mask_account_card, get_date

account_card = input(str("Введите номер счета или карты "))

print(mask_account_card(account_card))

user_date = input(str("Введите дату "))

print(get_date(user_date))
