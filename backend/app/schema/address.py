from pydantic import BaseModel
from typing import List

class SearchObject(BaseModel):
    locality: str
    street: str
    number: str
    lon: float
    lat: float
    score: float

class SearchResponse(BaseModel):
    searched_address: str
    objects: List[SearchObject]
