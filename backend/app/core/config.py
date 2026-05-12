from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "info"
    SECRET_KEY: str = "dev_secret_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://itl_user:password@localhost/in_the_life"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # NATS
    NATS_URL: str = "nats://localhost:4222"

    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    # ML
    MODEL_CACHE_DIR: str = "app/model_cache"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIM: int = 384

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",")]


settings = Settings()
