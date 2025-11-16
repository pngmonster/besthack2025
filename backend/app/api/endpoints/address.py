from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from typing import List
from app.utils.model import search_address_single_levenshtein
from app.schema.address import SearchResponse


router = APIRouter(prefix="/search", tags=["search"])

@router.get("", response_model=SearchResponse)
async def search(address: str):
    try:
        res = search_address_single_levenshtein("buildings_cleaned.csv", address, top_n=3)
        return res

    except Exception as e:
        print("❌ Ошибка при сохранении:", e)
        raise HTTPException(status_code=500, detail=f"Error calculating route: {str(e)}")
