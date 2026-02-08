import os
from typing import Dict, List

import pandas as pd

# Указываем путь к CSV файлу
csv_path = r"D:\shcool\pythonProject1\data\transactions.csv"


def read_csv_operations(csv_path: str) -> List[Dict[str, any]]:
    """Считывает финансовые операции из CSV‑файла и возвращает список словарей."""
    # Проверяем существование файла
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Файл не найден: {csv_path}")

    try:
        # Читаем CSV
        df = pd.read_csv(csv_path, encoding='utf-8')

        # Проверяем, что данные есть
        if df.empty:
            raise pd.errors.EmptyDataError("Файл пуст.")

        # Преобразуем в список словарей
        transactions = df.to_dict(orient='records')
        return transactions

    except pd.errors.EmptyDataError as e:
        raise e
    except pd.errors.ParserError as e:
        raise pd.errors.ParserError(f"Ошибка парсинга CSV: {e}")
    except Exception as e:
        raise Exception(f"Неожиданная ошибка при чтении CSV: {e}")


# Указываем путь к EXCEL файлу
excel_path = r"D:\shcool\pythonProject1\data\transactions_excel.xlsx"


def read_excel_operations(excel_path: str) -> List[Dict[str, any]]:
    """Считывает финансовые операции из Excel‑файла (.xlsx) и возвращает список словарей."""
    # Проверяем существование файла
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Файл не найден: {excel_path}")

    try:
        # Читаем Excel (первый лист по умолчанию)
        df = pd.read_excel(excel_path)

        # Проверяем, что данные есть
        if df.empty:
            raise ValueError("Файл Excel пуст.")

        # Преобразуем в список словарей
        transactions = df.to_dict(orient='records')
        return transactions

    except ValueError as e:
        if "No sheet" in str(e):
            raise ValueError("В файле Excel нет листов.")
        else:
            raise e
    except Exception as e:
        raise Exception(f"Неожиданная ошибка при чтении Excel: {e}")
