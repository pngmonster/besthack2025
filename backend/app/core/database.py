from typing import AsyncGenerator
import chromadb
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import configs
from app.model.base_model import Base
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
engine = create_async_engine(configs.DATABASE_URI, echo=False, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

chroma = chroma_client = chromadb.Client()
model = SentenceTransformer(MODEL_NAME)

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
