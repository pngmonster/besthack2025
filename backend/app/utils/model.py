import pandas as pd
from rapidfuzz import process, fuzz

def search_address_single(csv_path, query, top_n=3):
    """
    Поиск топ-N совпадений для одного запроса, возвращает словарь в JSON-подобной структуре.

    Параметры:
        csv_path: путь к CSV с колонкой 'full_address', '@id', '@lat', '@lon'
        query: строка запроса
        top_n: сколько лучших совпадений возвращать

    Возвращает:
        Словарь с ключами:
            - searched_address: исходный запрос
            - objects: список совпадений
    """
    # Загружаем CSV
    df = pd.read_csv(csv_path, sep=';')

    # Нормализация запроса
    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm
    query_norm_lower = query_norm.lower()

    # Поиск топ-N совпадений
    matches = process.extract(query_norm_lower, df['full_address'].str.lower(), scorer=fuzz.WRatio, limit=top_n)

    # Функция разбора full_address на улицу и номер
    def parse_address(full_address):
        parts = full_address.replace("Москва,", "").strip().split(",", 1)
        street = parts[0].strip() if len(parts) > 0 else ""
        number = parts[1].strip() if len(parts) > 1 else ""
        return street, number

    objects = []
    for m in matches:
        idx = m[2]
        score = m[1] / 100  # нормируем в 0-1
        row = df.iloc[idx]
        street, number = parse_address(row['full_address'])
        objects.append({
            "locality": "Москва",
            "street": street,
            "number": number,
            "lon": row['@lon'],
            "lat": row['@lat'],
            "score": score
        })

    return {
        "searched_address": query,
        "objects": objects
    }
