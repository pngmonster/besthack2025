from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    id: int
    node_id: int
    localy: str
    street: str
    number: str
    lat: float
    lon: float

    model_config = {"from_attributes": True}


class AddressCreate(BaseModel):
    node_id: int
    localy: str
    street: str
    number: str
    lat: float
    lon: float
    embedding: List[float]

    model_config = {"from_attributes": True}

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
