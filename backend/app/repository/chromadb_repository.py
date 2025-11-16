import chromadb
from typing import List
from fastapi import Depends
from app.core.database import get_chroma
from sentence_transformers import SentenceTransformer

class ChromaRepository:
    def __init__(self, collection: chromadb.Collection):
        self.collection = collection

    async def add(self, ids: List[str], texts: List[str], embedding: List[float]):
        self.collection.add(ids=ids, documents=texts, embeddings=embedding)

    async def query(self, search_address: str, n_results: int):
        MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        model = SentenceTransformer(MODEL_NAME)
        emb = model.encode(
               search_address,
               convert_to_numpy=False,   # возвращает torch.Tensor
           )
        result = self.collection.query(
            query_embeddings=[emb],
            n_results=n_results,
        )
        ids = result["ids"][0]
        distances = result["distances"][0]
        return (ids, distances)

def get_chroma_repo(coll: chromadb.Collection = Depends(get_chroma)) -> ChromaRepository:
    return ChromaRepository(coll)
