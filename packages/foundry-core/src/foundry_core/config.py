"""Typed settings for all Foundry services (loaded from env)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Shared runtime configuration.

    All Foundry services (api, worker, scripts) should call `get_settings()`
    instead of reading environment variables directly.
    """

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Environment -------------------------------------------------------
    env: str = Field(default="development", alias="FOUNDRY_ENV")
    log_level: str = Field(default="INFO", alias="FOUNDRY_LOG_LEVEL")
    secret_key: str = Field(default="dev-secret-change-me", alias="FOUNDRY_SECRET_KEY")

    # --- Database ----------------------------------------------------------
    database_url: str = Field(
        default="postgresql+asyncpg://foundry:foundry@localhost:5432/foundry",
        alias="DATABASE_URL",
    )
    database_url_sync: str = Field(
        default="postgresql+psycopg://foundry:foundry@localhost:5432/foundry",
        alias="DATABASE_URL_SYNC",
    )

    # --- Redis / jobs ------------------------------------------------------
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # --- API ---------------------------------------------------------------
    api_host: str = Field(default="0.0.0.0", alias="FOUNDRY_API_HOST")
    api_port: int = Field(default=8000, alias="FOUNDRY_API_PORT")
    api_cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="FOUNDRY_API_CORS_ORIGINS",
    )

    # --- Repo storage ------------------------------------------------------
    repos_dir: Path = Field(
        default=Path("/var/lib/foundry/repos"),
        alias="FOUNDRY_REPOS_DIR",
    )

    # --- Stale thresholds --------------------------------------------------
    stale_days_warn: int = Field(default=14, alias="FOUNDRY_STALE_DAYS_WARN")
    stale_days_critical: int = Field(default=45, alias="FOUNDRY_STALE_DAYS_CRITICAL")

    @field_validator("api_cors_origins")
    @classmethod
    def _normalize_origins(cls, v: str) -> str:
        return ",".join(part.strip() for part in v.split(",") if part.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [o for o in self.api_cors_origins.split(",") if o]

    @property
    def is_production(self) -> bool:
        return self.env.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
