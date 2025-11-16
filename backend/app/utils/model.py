import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz

# Нормализация улиц
street_types = {
    r'\bул\.?\b': 'улица',
    r'\bпер\.?\b': 'переулок',
    r'\bпр-т\b': 'проспект',
    r'\bб-р\b': 'бульвар',
    r'\bш\b': 'шоссе'
}

def normalize_street_name(street_name):
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

def search_address_single(df, query, top_n=3):
    # Нормализация запроса
    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm

    # Разбор на улицу и номер дома
    match = re.search(r'\d+[а-яА-ЯкК]*', query_norm)
    query_house = match.group(0) if match else ""
    street_query = re.sub(r'\d+[а-яА-ЯкК]*', '', query_norm).replace("Москва,", "").strip().lower()

    # Нормализация всех улиц
    df['street_norm'] = df['street'].apply(normalize_street_name).str.lower().str.strip()

    # Быстро отбираем кандидатов по подстроке (первые 3 символа запроса)
    prefix = street_query[:3]
    candidates = df[df['street_norm'].str.contains(prefix)]

    # Если слишком мало кандидатов, берём весь df
    if len(candidates) < 50:
        candidates = df

    # Векторизация fuzzy score через NumPy
    streets_np = candidates['street_norm'].to_numpy()
    query_np = np.array([street_query] * len(streets_np))
    vectorized_score = np.vectorize(fuzz.WRatio)(query_np, streets_np)

    top_idx = np.argsort(vectorized_score)[::-1][:top_n]
    results = []
    for i in top_idx:
        row = candidates.iloc[i]
        street_score = vectorized_score[i] / 100

        # Проверка номера дома
        number_score = 1.0
        if query_house:
            if query_house.lower() in str(row['house']).lower():
                number_score = 1.0
            else:
                number_score = 0.5

        final_score = (street_score + number_score) / 2

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

    return {
        "searched_address": query,
        "objects": results
    }
