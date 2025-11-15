from app.api.endpoints.address import router as address
from fastapi import APIRouter

main_router = APIRouter(prefix='/api')
main_router.include_router(address)
