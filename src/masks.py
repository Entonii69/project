def get_mask_card_number(number_card: str) -> str:
    """Функция которая маскирует номера карты"""
    # Удаляем все пробелы из исходного номера карты
    clean_number = number_card.replace(" ", "")

    # Проверяем корректность длины номера карты
    if len(clean_number) != 16:
        raise ValueError("Номер карты должен содержать ровно 16 цифр")

    # Проверяем посторонние символы в номере карты
    if not clean_number.isdigit():
        raise ValueError("Присутствие посторонних символов в номере карты")

    mask_number_card = clean_number[:4] + " " + clean_number[4:6] + "** **** " + clean_number[-4:]
    return mask_number_card


def get_mask_account(account: str) -> str:
    """Функция которая маскирует номер счета"""
    # Удаляем все пробелы из исходного номера
    clean_account = account.replace(" ", "")

    # Проверяем корректность длины номера счета
    if len(clean_account) != 20:
        raise ValueError("Номер карты должен содержать ровно 20 цифр")

    # Проверяем посторонние символы в номере счета
    if not clean_account.isdigit():
        raise ValueError("Присутствие посторонних символов в номере счета")

    mask_account = "**" + clean_account[-4:]
    return mask_account
