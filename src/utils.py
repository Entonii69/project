import json
import os

from typing import List, Dict


def load_financial_transactions(file_path: str) -> List[Dict]:
    """Загружает финансовые транзакции из JSON-файла."""
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []
