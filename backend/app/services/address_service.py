from typing import List
from fastapi import Depends
import Levenshtein
from app.repository.address_repository import AddressRepository, get_address_repo
from app.repository.chromadb_repository import ChromaRepository, get_chroma_repo
from app.schema.address import AddressCreate, Address, SearchResponse, SearchObject
import re
from app.utils.model import search_address_single

street_types = {
    "ул": "улица",
    "ул.": "улица",
    "пер": "переулок",
    "пер.": "переулок",
    "пр-т": "проспект",
    "пр.": "проспект",
    "ш": "шоссе",
    "бул": "бульвар",
    "пл": "площадь"
}


def normalize_address(raw_address: str, default_city="Москва") -> str:
    # Нижний регистр и удаление лишних символов
    addr = raw_address.lower()
    addr = re.sub(r"[.,]", "", addr)
    addr = re.sub(r"\s+", " ", addr).strip()

    # Ищем номер дома, корпуса и строения
    house_match = re.search(r"(\d+\s*[кс]?\d*)$", addr)
    house_part = house_match.group(1).strip() if house_match else ""

    # Убираем дом/корпус из основной строки
    street_part = addr[:house_match.start()].strip() if house_match else addr

    # Раскрываем сокращения улиц
    for abbr, full in street_types.items():
        street_part = re.sub(r"\b" + re.escape(abbr) + r"\b", full, street_part)

    # Приведение порядка слов: тип улицы в конце
    street_words = street_part.split()
    # Если первый элемент — тип улицы, перемещаем в конец
    if street_words and street_words[0] in street_types.values():
        street_words = street_words[1:] + [street_words[0]]
    street_part = " ".join(word.capitalize() for word in street_words)

    # Собираем нормализованную строку
    normalized = f"{default_city}, {street_part}"
    if house_part:
        normalized += f", {house_part}"

    return normalized

def compute_score(pred: str, true: str) -> float:
    pred_norm = normalize_address(pred)
    true_norm = normalize_address(true)
    print(pred_norm)
    print(true_norm)
    distance = Levenshtein.distance(pred_norm, true_norm)
    score = 1 - distance / max(len(pred_norm), len(true_norm))
    return max(0, score)

class AddressService:

    def __init__(self, address_repo: AddressRepository, chroma_repo: ChromaRepository):
        self.address_repo = address_repo
        self.chroma_repo = chroma_repo

    async def save(self, addresses: List[AddressCreate]):
        ids = []
        texts = []
        embedding = []
        for address in addresses:
            addressDB = await self.address_repo.create(address)
            ids.append(str(addressDB.id))
            texts.append(addressDB.localy+" "+addressDB.street+ " " + addressDB.number)
            embedding.append(address.embedding)
        await self.chroma_repo.add(ids, texts, embedding)

    async def search(self, search: str, n_results=5):
        res = search_address_single("addresses_full.csv", search, top_n=3)
        return res

def get_address_service(
        address_repo: AddressRepository = Depends(get_address_repo),
        chroma_repo: ChromaRepository = Depends(get_chroma_repo)) -> AddressService:
    return AddressService(address_repo, chroma_repo)
