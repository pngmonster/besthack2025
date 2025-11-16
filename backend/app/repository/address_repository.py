from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from fastapi import Depends

from app.core.database import get_session
from app.model.address import AddressModel
from app.schema.address import Address, AddressCreate

class AddressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, idx: int) -> Optional[Address]:
        result = await self.session.execute(select(AddressModel).where(AddressModel.id == idx))
        addressModel = result.scalar_one_or_none()
        address = Address.model_validate(addressModel)
        return address

    async def get_all(self) -> List[Address]:
        result = await self.session.execute(select(AddressModel))
        addresses = [Address.model_validate(i) for i in result.scalars().all()]
        return addresses

    async def create(self, address_create: AddressCreate) -> Address:
        try:
            addressModel = AddressModel(
                node_id=address_create.node_id,
                localy=address_create.localy,
                street=address_create.street,
                number=address_create.number,
                lat=address_create.lat,
                lon=address_create.lon
            )
            self.session.add(addressModel)
            await self.session.commit()
            await self.session.refresh(addressModel)
            address = Address.model_validate(addressModel)
            return address
        except Exception as e:
            await self.session.rollback()
            raise e

def get_address_repo(session: AsyncSession = Depends(get_session)) -> AddressRepository:
    return AddressRepository(session)
