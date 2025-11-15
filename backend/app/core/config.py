import os
from typing import List
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Configs(BaseSettings):
    API: str = "/api"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "backend"

    DB_ENGINE_MAPPER: dict = {
        "postgresql": "postgresql+asyncpg",
    }

    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # date
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"

    # auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 60 minutes * 24 hours * 30 days = 30 days

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # database
    DB: str = os.getenv("DB", "postgresql")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin")
    DB_HOST: str = os.getenv("DB_HOST", "postgres")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_ENGINE: str = DB_ENGINE_MAPPER.get("postgresql", "postgresql")

    DATABASE_URI: str = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB}"

    class Config:
        case_sensitive = True


configs = Configs()
