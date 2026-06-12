from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Resolve the repo-root .env by absolute path so settings load correctly no
# matter what working directory the API process starts from (e.g. uvicorn run
# from apps/api). A relative env_file='.env' silently falls back to defaults
# (demo_mode=True) when cwd != repo root, forcing the whole app into mock mode.
_REPO_ROOT = Path(__file__).resolve().parents[4]
_ENV_FILE = _REPO_ROOT / ".env"


class Settings(BaseSettings):
    app_env: str = "development"
    demo_mode: bool = True
    database_url: str = "sqlite:///./hxrizxn.db"
    api_cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    azure_foundry_project_endpoint: str | None = None
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2025-04-01-preview"

    foundry_iq_endpoint: str | None = None
    foundry_iq_api_key: str | None = None
    foundry_iq_index_name: str = "hxrizxn-demo"

    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    upload_dir: str = Field(default="uploads")
    azure_storage_connection_string: str | None = None
    azure_blob_container: str = "uploads"

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.api_cors_origins.split(",") if origin.strip()]

    @property
    def foundry_iq_configured(self) -> bool:
        return bool(self.foundry_iq_endpoint and self.foundry_iq_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
