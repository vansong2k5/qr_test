from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, BaseSettings, validator


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://qruser:qrpass@localhost:5432/qrdb"
    jwt_secret: str = "change_me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7
    cors_origins = ["http://localhost:5173"]
    redis_url: str = "redis://localhost:6379/0"
    file_storage: str = "./uploads"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @validator("cors_origins", pre=True)
    def split_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin]
        return v


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
