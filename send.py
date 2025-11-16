import json
import requests
from tqdm import tqdm

# ==== Настройки ====
INPUT_FILE = "output.json"
API_URL = "http://localhost:8000/api/search/save"
BATCH_SIZE = 500  # размер батча, можно менять
# ====================

# Загружаем JSON
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    items = json.load(f)

total = len(items)
print(f"Всего объектов: {total}")

# Функция отправки одного батча
def send_batch(batch, batch_id):
    try:
        resp = requests.post(
            API_URL,
            headers={
                "accept": "application/json",
                "Content-Type": "application/json"
            },
            json=batch
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"\nОшибка при отправке батча {batch_id}: {e}")

# Разбиваем на батчи и отправляем
for i in tqdm(range(0, total, BATCH_SIZE), desc="Отправка батчей"):
    batch = items[i:i + BATCH_SIZE]

    # гарантируем, что localy есть
    for item in batch:
        if not item.get("localy"):
            item["localy"] = "Москва"

    send_batch(batch, i // BATCH_SIZE)

print("Готово! Все объекты отправлены батчами.")
