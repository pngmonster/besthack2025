from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse
from fastapi.exceptions import HTTPException
from typing import List

from app.services.address_service import AddressService, get_address_service
from app.schema.address import AddressCreate, SearchResponse


router = APIRouter(prefix="/search", tags=["search"])

@router.post("/save")
async def save(addresses: List[AddressCreate],  service: AddressService = Depends(get_address_service)):
    try:
        await service.save(addresses)

        return JSONResponse("ok", 200)

    except Exception as e:
        print("❌ Ошибка при сохранении:", e)
        raise HTTPException(status_code=500, detail=f"Error calculating route: {str(e)}")

@router.get("", response_model=SearchResponse)
async def search(address: str, service: AddressService = Depends(get_address_service)):
    try:
        res = await service.search(address)

        return res

    except Exception as e:
        print("❌ Ошибка при сохранении:", e)
        raise HTTPException(status_code=500, detail=f"Error calculating route: {str(e)}")
