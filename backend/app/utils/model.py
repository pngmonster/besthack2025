import pandas as pd
from rapidfuzz import process, fuzz

import pandas as pd
from rapidfuzz import process, fuzz
import re

# Словарь для замены сокращений
street_types = {
    r'\bул\.?\b': 'улица',
    r'\bпер\.?\b': 'переулок',
    r'\bпр-т\b': 'проспект',
    r'\bб-р\b': 'бульвар',
    r'\bш\b': 'шоссе'
}

def normalize_street_name(street_name):
    """
    Нормализует название улицы: заменяет сокращения и приводит к нормативному порядку слов.
    """
    name = street_name.lower().strip()
    for abbr, full in street_types.items():
        name = re.sub(abbr, full, name)
    tokens = name.split()
    street_type = None
    for t in ['улица', 'переулок', 'проспект', 'бульвар', 'шоссе']:
        if t in tokens:
            street_type = t
            tokens.remove(t)
            break
    if street_type:
        normalized = ' '.join(tokens).capitalize() + ' ' + street_type
    else:
        normalized = ' '.join(tokens).capitalize()
    return normalized

def format_full_address(city, street, house, building='', structure=''):
    street_norm = normalize_street_name(street)
    parts = [city, street_norm, house]
    if building:
        parts.append(building)
    if structure:
        parts.append(structure)
    return ', '.join(parts[:2]) + ', ' + ' '.join(parts[2:])

def search_address_single(csv_path, query, top_n=3):
    """
    Поиск топ-N совпадений для одного запроса с нормализацией адреса.
    """
    df = pd.read_csv(csv_path, sep=';')

    # Нормализуем запрос
    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm

    # Выделяем номер дома из запроса
    match = re.search(r'\d+[а-яА-ЯкК]*', query_norm)
    query_house = match.group(0) if match else ""
    # Выделяем улицу
    street_query = re.sub(r'\d+[а-яА-ЯкК]*', '', query_norm).replace("Москва,", "").strip().lower()

    # Нормализуем все улицы в df
    df['street_norm'] = df['street'].apply(normalize_street_name).str.lower().str.strip()

    # Fuzzy поиск улицы
    street_matches = process.extract(street_query, df['street_norm'], scorer=fuzz.WRatio, limit=len(df))

    results = []
    for street_name, street_score, idx in street_matches:
        row = df.iloc[idx]
        # Проверка номера дома
        number_score = 1.0
        if query_house:
            if query_house.lower() in str(row['house']).lower():
                number_score = 1.0
            else:
                number_score = 0.5
        final_score = (street_score / 100 + number_score) / 2

        full_address = format_full_address(
            city="Москва",
            street=row['street'],
            house=row['house'],
            building=row.get('building', ''),
            structure=row.get('structure', '')
        )

        results.append({
            "locality": "Москва",
            "street": normalize_street_name(row['street']),
            "number": row['house'],
            "full_address": full_address,
            "lon": row['@lon'],
            "lat": row['@lat'],
            "score": final_score
        })

    results = sorted(results, key=lambda x: x['score'], reverse=True)[:top_n]

    return {
        "searched_address": query,
        "objects": results
    }
