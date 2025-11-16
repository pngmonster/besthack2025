import pandas as pd
import numpy as np
import re
from rapidfuzz import fuzz, process
import functools

# Кэшируем нормализацию
@functools.lru_cache(maxsize=10000)
def normalize_street_name_cached(street_name):
    """Кэшированная версия нормализации названий улиц"""
    if not street_name or pd.isna(street_name):
        return ""

    name = str(street_name).lower().strip()

    # Быстрые замены через строковые методы
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

    # Быстрая проверка типов улиц
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
    """Предобработка DataFrame для ускорения поиска"""
    df = df.copy()

    # Предварительно нормализуем все улицы
    if 'street_normalized' not in df.columns:
        df['street_normalized'] = df['street'].apply(normalize_street_name_cached).str.lower().str.strip()

    # Создаем поисковый индекс
    street_index = df['street_normalized'].tolist()

    return df, street_index

def search_address_single_fast(csv_path, query, top_n=3):
    """
    Оптимизированная версия поиска адресов
    """
    # Загружаем и предобрабатываем данные один раз
    if not hasattr(search_address_single_fast, '_df_cache'):
        df = pd.read_csv(csv_path, sep=';')
        search_address_single_fast._df_cache, search_address_single_fast._street_index = preprocess_dataframe(df)

    df = search_address_single_fast._df_cache
    street_index = search_address_single_fast._street_index

    # Быстрая нормализация запроса
    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm

    # Быстрое извлечение номера дома
    house_match = re.search(r'\d+[а-яА-ЯкК]*', query_norm)
    query_house = house_match.group(0) if house_match else ""

    # Извлекаем улицу из запроса
    street_query = re.sub(r'\d+[а-яА-ЯкК]*', '', query_norm)\
                      .replace("Москва,", "")\
                      .strip()\
                      .lower()

    # Используем rapidfuzz.process для быстрого поиска лучших совпадений
    matches = process.extract(
        street_query,
        street_index,
        scorer=fuzz.WRatio,
        limit=top_n * 3,  # Берем больше для фильтрации по дому
        score_cutoff=50   # Минимальный порог совпадения
    )

    results = []
    for street_norm, score, idx in matches:
        row = df.iloc[idx]

        # Проверка номера дома (только если указан в запросе)
        number_score = 1.0
        if query_house:
            house_str = str(row['house']).lower()
            if query_house.lower() == house_str:
                number_score = 1.0
            elif query_house.lower() in house_str:
                number_score = 0.8
            else:
                number_score = 0.3  # Штраф за несовпадение дома

        street_score = score / 100
        final_score = (street_score + number_score) / 2

        # Формируем полный адрес
        full_address = f"Москва, {normalize_street_name_cached(row['street'])}, {row['house']}"
        building = row.get('building', '')
        structure = row.get('structure', '')

        if building and not pd.isna(building):
            full_address += f" {building}"
        if structure and not pd.isna(structure):
            full_address += f" {structure}"

        results.append({
            "locality": "Москва",
            "street": normalize_street_name_cached(row['street']),
            "number": row['house'],
            "lon": row['@lon'],
            "lat": row['@lat'],
            "score": final_score
        })

    # Сортируем по убыванию score и берем top_n
    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:top_n]

    return {
        "searched_address": query,
        "objects": results
    }
