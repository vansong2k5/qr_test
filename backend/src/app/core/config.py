"""Cấu hình ứng dụng sử dụng Pydantic Settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseSettings, Field, PostgresDsn, RedisDsn, validator


class Settings(BaseSettings):
    env: str = Field(default="development", env="ENV")
    api_prefix: str = "/api"
    project_name: str = "QR Lifecycle Platform"
    docs_url: str = "/docs"
    openapi_url: str = "/openapi.json"
    root_path: Path = Field(default_factory=lambda: Path(__file__).resolve().parents[3])

    database_url: PostgresDsn = Field(
        default="postgresql+psycopg2://postgres:postgres@db:5432/qr", env="DATABASE_URL"
    )
    redis_url: RedisDsn = Field(default="redis://redis:6379/0", env="REDIS_URL")

    jwt_secret_key: str = Field(default="super-secret-key", min_length=16, env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    upload_dir: Path = Field(default_factory=lambda: Path("/data/uploads"))
    rate_limit_scan_per_minute: int = Field(default=30, env="RATE_LIMIT_SCAN_PER_MINUTE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        allow_population_by_field_name = True

    @validator("upload_dir", pre=True)
    def _ensure_path(cls, value: Any) -> Path:  # type: ignore[override]
        if isinstance(value, Path):
            return value
        return Path(str(value))


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()
