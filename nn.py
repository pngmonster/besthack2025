import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# ==== Настройки ====
INPUT_FILE = "output.json"       # входной JSON
OUTPUT_FILE = "output_with_emb.json"
MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"
# ====================

# Загружаем данные
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

# Загружаем модель
model = SentenceTransformer(MODEL_NAME)

# Генерация эмбеддингов
for item in tqdm(items, desc="Generating embeddings"):
    # Формируем полный адрес
    full_address = f"{item.get('localy','')} {item.get('street','')} {item.get('number','')}"

    # Получаем эмбеддинг
    embedding = model.encode(full_address, convert_to_numpy=True).tolist()

    # Добавляем в объект
    item["embedding"] = embedding

# Сохраняем результат
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Эмбеддинги сохранены в {OUTPUT_FILE}")
