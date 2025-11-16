import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz, process
import functools

# Кэшируем нормализацию (только для поиска)
@functools.lru_cache(maxsize=10000)
def normalize_street_name_cached(street_name):
    """Кэшированная версия нормализации названий улиц ТОЛЬКО для поиска"""
    if not street_name or pd.isna(street_name):
        return ""

    name = str(street_name).lower().strip()

    replacements = [
        ('ул.', 'улица'), ('ул ', 'улица '), (' ул ', ' улица '),
        ('пер.', 'переулок'), ('пер ', 'переулок '), (' пер ', ' переулок '),
        ('пр-т', 'проспект'), ('пр т', 'проспект'), (' пр-т ', ' проспект '),
        ('б-р', 'бульвар'), ('б р', 'бульвар'), (' б-р ', ' бульвар '),
        (' ш ', ' шоссе ')
    ]

    for old, new in replacements:
        name = name.replace(old, new)

    tokens = name.split()
    street_type = None

    street_types_set = {'улица', 'переулок', 'проспект', 'бульвар', 'шоссе'}
    for i, token in enumerate(tokens):
        if token in street_types_set:
            street_type = token
            tokens.pop(i)
            break

    if street_type:
        normalized = ' '.join(tokens).capitalize() + ' ' + street_type
    else:
        normalized = ' '.join(tokens).capitalize()

    return normalized


def preprocess_dataframe(df):
    """Подготовка DataFrame специально под твою таблицу"""

    df = df.copy()

    # ⛔ ОРИГИНАЛ — addr:street и addr:housenumber
    df["street_original"] = df["addr:street"]
    df["house_original"] = df["addr:housenumber"]

    # Нормализуем колонку street (которая у тебя lowercase)
    df["street_normalized"] = df["street"].apply(normalize_street_name_cached).str.lower().str.strip()

    # Поисковый индекс
    street_index = df["street_normalized"].tolist()

    return df, street_index


def calculate_levenshtein_score(street_query, street_candidate, house_query, house_candidate):
    house_candidate_str = str(house_candidate).lower().strip() if not pd.isna(house_candidate) else ""
    house_query_str = house_query.lower().strip() if house_query else ""

    if street_query and street_candidate:
        street_similarity = fuzz.ratio(street_query, street_candidate, processor=None)
        street_score = street_similarity / 100
    else:
        street_score = 0.0

    if house_query_str and house_candidate_str:
        if house_query_str == house_candidate_str:
            house_score = 1.0
        else:
            house_similarity = fuzz.ratio(house_query_str, house_candidate_str, processor=None)
            house_score = house_similarity / 100
    else:
        house_score = 0.5 if not house_query_str else 0.0

    if house_query_str:
        return 0.7 * street_score + 0.3 * house_score
    else:
        return street_score


def search_address_single_levenshtein(csv_path, query, top_n=3):
    if not hasattr(search_address_single_levenshtein, "_df_cache"):
        df = pd.read_csv(csv_path, sep=";")
        search_address_single_levenshtein._df_cache, search_address_single_levenshtein._street_index = preprocess_dataframe(df)

    df = search_address_single_levenshtein._df_cache
    street_index = search_address_single_levenshtein._street_index

    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm

    house_match = re.search(r'\d+[а-яА-ЯкК/\-]*', query_norm)
    query_house = house_match.group(0) if house_match else ""

    street_query = (
        re.sub(r'\d+[а-яА-ЯкК/\-]*', '', query_norm)
        .replace("Москва,", "")
        .replace("москва,", "")
        .strip()
        .lower()
    )

    street_query_norm = normalize_street_name_cached(street_query).lower()

    matches = process.extract(
        street_query_norm,
        street_index,
        scorer=fuzz.ratio,
        limit=top_n * 5,
        score_cutoff=30
    )

    results = []

    for street_norm, street_similarity, idx in matches:
        row = df.iloc[idx]

        final_score = calculate_levenshtein_score(
            street_query_norm,
            street_norm,
            query_house,
            row["house_original"]
        )

        results.append({
            "locality": "Москва",
            "street": row["street_original"],   # ОРИГИНАЛ
            "number": row["house_original"],     # ОРИГИНАЛ
            "lon": float(row["@lon"]),
            "lat": float(row["@lat"]),
            "score": final_score,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:top_n]

    return {
        "searched_address": query,
        "objects": results
    }
