import json
import requests
from tqdm import tqdm

# ==== Настройки ====
INPUT_FILE = "output.json"
API_URL = "http://localhost:8000/api/search/save"
# ====================

# Загружаем JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

# Отправляем каждый объект отдельно
for i, item in enumerate(tqdm(items, desc="Sending items")):
    if not item["localy"]: item["localy"]="Москва"

    try:
        response = requests.post(
            API_URL,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=[item]  # оборачиваем в список, т.к. API ожидает массив
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"\nError sending item {i}: {e}")
    else:
        pass  # можно добавить: print(f"Item {i} sent, status {response.status_code}")

print("Все объекты отправлены!")
