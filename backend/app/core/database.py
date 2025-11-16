from typing import AsyncGenerator
import chromadb
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import configs
from app.model.base_model import Base


engine = create_async_engine(configs.DATABASE_URI, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

chroma = chroma_client = chromadb.HttpClient(host='localhost', port=8001)

collection = chroma.create_collection(
    name="addresses",
)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession]:
    async with async_session_maker() as session:
        yield session

async def get_chroma() -> chromadb.Collection:
    return collection