import pandas as pd
from rapidfuzz import process, fuzz

# Загружаем CSV с полной колонкой адресов
df = pd.read_csv("addresses_full.csv", sep=';')

# Функция для нормализации запроса
def normalize_query(query):
    query = query.strip()
    if not query.lower().startswith("москва"):
        query = "Москва, " + query
    return query.lower()

# Функция поиска топ-N совпадений
def find_top_addresses(query, df, top_n=3):
    query_norm = normalize_query(query)

    # Поиск топ-N совпадений
    matches = process.extract(query_norm, df['full_address'].str.lower(), scorer=fuzz.WRatio, limit=top_n)

    results = []
    for match in matches:
        addr_idx = match[2]
        score = match[1]
        row = df.iloc[addr_idx]
        results.append({
            "query": query,
            "normalized_query": query_norm,
            "best_match": row['full_address'],
            "score": score,
            "id": row['@id'],
            "lat": row['@lat'],
            "lon": row['@lon']
        })
    return results

# Пример поиска
queries = ["выборгская 24", "улица дурова 4", "крутицкий вал 26 с2"]

all_results = []
for q in queries:
    all_results.extend(find_top_addresses(q, df, top_n=3))

# Выводим результаты
for r in all_results:
    print(r)
