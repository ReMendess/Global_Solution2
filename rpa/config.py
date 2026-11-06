"""Configuração do RPA (12-factor, via variáveis de ambiente e .env).

Reutiliza os mesmos nomes de variáveis do backend (`API_BASE_URL`, `RPA_PORTAL_URL`,
`RPA_HEADLESS`) definidos em `.env.example`.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# rpa/config.py -> parents[0]=rpa, parents[1]=raiz do repositório.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Configurações do robô e do portal."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- backend API ---
    api_base_url: str = "http://127.0.0.1:8000"

    # --- portal administrativo fictício ---
    rpa_portal_url: str = "http://127.0.0.1:8100"
    rpa_headless: bool = True

    # --- caminhos de artefatos ---
    screenshots_dir: Path = Path("./rpa/screenshots")
    reports_dir: Path = Path("./rpa/reports")

    # --- limites ---
    # Número máximo de demandas processadas por execução (None = todas).
    max_demands: int | None = None
    request_timeout_seconds: float = 10.0

    @property
    def queue_endpoint(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/api/v1/rpa/queue"

    @property
    def executions_endpoint(self) -> str:
        return f"{self.api_base_url.rstrip('/')}/api/v1/rpa/executions"

    @property
    def resolved_screenshots_dir(self) -> Path:
        return self._resolve(self.screenshots_dir)

    @property
    def resolved_reports_dir(self) -> Path:
        return self._resolve(self.reports_dir)

    def _resolve(self, caminho: Path) -> Path:
        return caminho if caminho.is_absolute() else (PROJECT_ROOT / caminho)


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única de configuração do RPA."""
    return Settings()
