import chromadb
from typing import List
from fastapi import Depends
from app.core.database import get_chroma

class ChromaRepository:
    def __init__(self, collection: chromadb.Collection):
        self.collection = collection

    async def add(self, ids: List[str], texts: List[str]):
        self.collection.add(ids=ids, documents=texts)

    async def query(self, search_address: str, n_results: int):
        result = self.collection.query(
            query_texts=search_address,
            n_results=n_results
        )
        ids = result["ids"][0]
        distances = result["distances"][0]
        return (ids, distances)

def get_chroma_repo(coll: chromadb.Collection = Depends(get_chroma)) -> ChromaRepository:
    return ChromaRepository(coll)
