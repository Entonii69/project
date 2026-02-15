import re
from typing import List, Dict, Any


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """
    Ищет в списке операций те, у которых в поле 'description' есть подстрока,
    соответствующая регулярному выражению `search`.
    Поиск регистронезависимый.
    """
    pattern = re.compile(search, re.IGNORECASE)
    result = []
    for item in data:
        description = item.get('description', '')
        if pattern.search(description):
            result.append(item)
    return result


def process_bank_operations(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """
    Подсчитывает количество операций в каждой из указанных категорий.
    Категория определяется по наличию подстроки в поле 'description'.
    """
    result = {category: 0 for category in categories}
    for item in data:
        desc = item.get('description', '').lower()
        for category in categories:
            if category.lower() in desc:
                result[category] += 1
    return result
