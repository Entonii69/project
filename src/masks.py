import logging

# Полный путь к файлу логов
log_masks_path = r"D:\shcool\pythonProject1\logs\masks.log"

logging.basicConfig(
    filename=log_masks_path,
    filemode='a',           # режим: 'a' (дописывать) или 'w' (перезаписывать)
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

logger = logging.getLogger(__name__)


def get_mask_card_number(number_card: str) -> str:
    """Функция которая маскирует номера карты"""
    # Удаляем все пробелы из исходного номера карты
    clean_number = number_card.replace(" ", "")
    logger.info("Пробелы удалены. Очищенный номер: %s", clean_number)

    # Проверка длины
    if len(clean_number) != 16:
        logger.error(
            "Некорректная длина номера карты: %d символов (ожидается 16). Номер: %s",
            len(clean_number), clean_number
        )
        raise ValueError("Номер карты должен содержать ровно 16 цифр")

    # Проверка на цифры
    if not clean_number.isdigit():
        logger.error("Обнаружены посторонние символы в номере карты: %s", clean_number)
        raise ValueError("Присутствие посторонних символов в номере карты")

    # Формирование маски
    mask_number_card = (clean_number[:4] + " " + clean_number[4:6] + "** **** " + clean_number[-4:])
    logger.info("Номер карты успешно замаскирован: %s", mask_number_card)
    return mask_number_card


def get_mask_account(account: str) -> str:
    """Функция которая маскирует номер счета"""
    # Удаляем все пробелы из исходного номера
    clean_account = account.replace(" ", "")
    logger.info("Пробелы удалены. Очищенный номер счёта: %s", clean_account)

    # Проверка длины
    if len(clean_account) != 20:
        logger.error(
            "Некорректная длина номера счёта: %d символов (ожидается 20). Номер: %s",
            len(clean_account), clean_account
        )
        raise ValueError("Номер счёта должен содержать ровно 20 цифр")

    # Проверка на цифры
    if not clean_account.isdigit():
        logger.error("Обнаружены посторонние символы в номере счёта: %s", clean_account)
        raise ValueError("Присутствие посторонних символов в номере счёта")

    # Формирование маски
    mask_account = "**" + clean_account[-4:]
    logger.info("Номер счёта успешно замаскирован: %s", mask_account)
    return mask_account
