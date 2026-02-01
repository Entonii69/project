import os

import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_URL = "https://api.apilayer.com/exchangerates_data/convert?to={to}&from={from_}&amount={amount}"
CURRENCY = ["USD", "EUR"]


def convert_to_rubles(transaction: dict) -> float:
    """Конвертирует сумму транзакции в рубли через API"""
    amount = transaction.get("operationAmount", {}).get("amount", 0.0)
    currency = transaction.get("operationAmount", {}).get("currency", {}).get("code")

    if currency == "RUB":
        return amount

    elif currency in CURRENCY:
        try:
            response = requests.get(
                API_URL.format(to="RUB", from_=currency, amount=amount), headers={"apikey": API_KEY},
            )
            if response.status_code == 200:
                data = response.json()
                # Проверяем наличие ключа 'result'
                if "result" in data:
                    return data["result"]
                else:
                    print("В ответе API отсутствует ключ 'result'")
                    return 0.0
            else:
                print(f"Ошибка при конвертации валюты: {response.status_code} {response.text}")
                return 0.0
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при конвертации валюты:{e}")
            return 0.0
    else:
        return 0.0
