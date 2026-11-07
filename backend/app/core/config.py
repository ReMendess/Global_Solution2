"""Configuração central da aplicação (12-factor via variáveis de ambiente)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py -> parents[0]=core, [1]=app, [2]=backend, [3]=raiz do repositório.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

SQLITE_PREFIX = "sqlite:///"


class Settings(BaseSettings):
    """Configurações carregadas do arquivo .env e de variáveis de ambiente."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- aplicação ---
    app_env: str = "development"
    app_name: str = "Cidade Limpa API"
    app_version: str = "0.1.0"

    # --- banco de dados ---
    database_url: str = f"{SQLITE_PREFIX}./data/cidade_limpa.db"

    # --- uploads ---
    upload_dir: Path = Path("./data/uploads")
    max_upload_mb: int = Field(default=20, gt=0, le=50)

    # --- machine learning (FASE 3) ---
    model_path: Path = Path("./ml/models/cidade_limpa_mobilenetv2.keras")
    model_metadata_path: Path = Path("./ml/models/cidade_limpa_mobilenetv2.metadata.json")
    confidence_threshold: float = Field(default=0.70, ge=0.0, le=1.0)

    # --- integrações ---
    api_base_url: str = "http://127.0.0.1:8000"
    sensor_interval_seconds: int = Field(default=10, gt=0)
    rpa_portal_url: str = "http://127.0.0.1:8100"
    rpa_headless: bool = True

    # --- CORS (frontend Expo web/mobile) ---
    cors_origins: list[str] = ["*"]

    @property
    def resolved_upload_dir(self) -> Path:
        """Diretório de uploads resolvido a partir da raiz do repositório."""
        return (
            self.upload_dir
            if self.upload_dir.is_absolute()
            else (PROJECT_ROOT / self.upload_dir).resolve()
        )

    @property
    def resolved_database_url(self) -> str:
        """URL do banco com caminho absoluto, independente do diretório de execução."""
        if not self.database_url.startswith(SQLITE_PREFIX):
            return self.database_url

        raw_path = self.database_url[len(SQLITE_PREFIX) :]
        path = Path(raw_path)
        if not path.is_absolute():
            path = (PROJECT_ROOT / raw_path).resolve()
        return f"{SQLITE_PREFIX}{path.as_posix()}"

    @property
    def max_upload_bytes(self) -> int:
        """Limite de upload convertido para bytes."""
        return self.max_upload_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única de configuração (uso em toda a aplicação)."""
    return Settings()
