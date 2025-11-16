from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import HTTPException
from typing import List
import json
from app.utils.model import search_address_single
from app.schema.address import AddressCreate, SearchResponse


router = APIRouter(prefix="/search", tags=["search"])

@router.get("", response_model=SearchResponse)
async def search(address: str):
    try:
        res = search_address_single("addresses_full.csv", search, top_n=3)
        return json.dumps(res, ensure_ascii=False, indent=2)

    except Exception as e:
        print("❌ Ошибка при сохранении:", e)
        raise HTTPException(status_code=500, detail=f"Error calculating route: {str(e)}")
