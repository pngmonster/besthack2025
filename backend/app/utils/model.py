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

def calculate_levenshtein_score(street_query, street_candidate, house_query, house_candidate):
    """
    Расчет общего score на основе расстояния Левенштейна
    """
    # Нормализуем дома для сравнения
    house_candidate_str = str(house_candidate).lower().strip() if not pd.isna(house_candidate) else ""
    house_query_str = house_query.lower().strip() if house_query else ""

    # Score для улицы (расстояние Левенштейна)
    if street_query and street_candidate:
        # Используем normalized Levenshtein similarity (0-100)
        street_similarity = fuzz.ratio(street_query, street_candidate, processor=None)
        street_score = street_similarity / 100  # Приводим к 0-1
    else:
        street_score = 0.0

    # Score для дома
    if house_query_str and house_candidate_str:
        if house_query_str == house_candidate_str:
            house_score = 1.0
        else:
            # Для дома тоже используем Левенштейн, но с меньшим весом
            house_similarity = fuzz.ratio(house_query_str, house_candidate_str, processor=None)
            house_score = house_similarity / 100
    else:
        house_score = 0.5 if not house_query_str else 0.0  # Если дома нет в запросе, нейтральный score

    # Комбинируем scores (можно настроить веса)
    if house_query_str:  # Если дом указан в запросе
        final_score = 0.7 * street_score + 0.3 * house_score
    else:  # Если дом не указан
        final_score = street_score

    return final_score

def search_address_single_levenshtein(csv_path, query, top_n=3):
    """
    Поиск адресов с использованием расстояния Левенштейна
    """
    # Загружаем и предобрабатываем данные один раз
    if not hasattr(search_address_single_levenshtein, '_df_cache'):
        df = pd.read_csv(csv_path, sep=';')
        search_address_single_levenshtein._df_cache, search_address_single_levenshtein._street_index = preprocess_dataframe(df)

    df = search_address_single_levenshtein._df_cache
    street_index = search_address_single_levenshtein._street_index

    # Быстрая нормализация запроса
    query_norm = query.strip()
    if not query_norm.lower().startswith("москва"):
        query_norm = "Москва, " + query_norm

    # Извлекаем номер дома и улицу
    house_match = re.search(r'\d+[а-яА-ЯкК/\-]*', query_norm)
    query_house = house_match.group(0) if house_match else ""

    # Извлекаем улицу (убираем Москву и номер дома)
    street_query = re.sub(r'\d+[а-яА-ЯкК/\-]*', '', query_norm)\
                      .replace("Москва,", "")\
                      .replace("москва,", "")\
                      .strip()\
                      .lower()

    # Нормализуем запрос улицы
    street_query_norm = normalize_street_name_cached(street_query).lower()

    # Используем rapidfuzz.process с расстоянием Левенштейна
    matches = process.extract(
        street_query_norm,
        street_index,
        scorer=fuzz.ratio,  # Чистое расстояние Левенштейна
        limit=top_n * 5,    # Берем больше кандидатов для точной фильтрации
        score_cutoff=30     # Минимальный порог схожести
    )

    results = []
    for street_norm, street_similarity, idx in matches:
        row = df.iloc[idx]

        # Рассчитываем общий score с учетом дома
        final_score = calculate_levenshtein_score(
            street_query_norm,
            street_norm,
            query_house,
            row['house']
        )

        # Формируем полный адрес из оригинальных данных
        full_address_parts = []

        # Город (всегда Москва)
        full_address_parts.append("Москва")

        # Улица (оригинальное значение из DataFrame)
        full_address_parts.append(str(row['street']))

        # Дом (оригинальное значение из DataFrame)
        full_address_parts.append(str(row['house']))

        # Корпус/строение (оригинальные значения из DataFrame)
        building = row.get('building', '')
        if building and not pd.isna(building) and str(building) != 'nan' and str(building) != '':
            full_address_parts.append(str(building))

        structure = row.get('structure', '')
        if structure and not pd.isna(structure) and str(structure) != 'nan' and str(structure) != '':
            full_address_parts.append(str(structure))

        # Собираем полный адрес в оригильном формате
        full_address = ', '.join(full_address_parts[:2]) + ', ' + ' '.join(full_address_parts[2:])

        results.append({
            "locality": "Москва",
            "street": str(row['street']),  # Оригинальное название улицы
            "number": str(row['house']),   # Оригинальный номер дома
            "full_address": full_address,  # Адрес из оригильных данных
            "lon": float(row['@lon']),
            "lat": float(row['@lat']),
            "score": final_score,
        })

    # Сортируем по убыванию общего score
    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:top_n]

    return {
        "searched_address": query,
        "objects": results
    }
