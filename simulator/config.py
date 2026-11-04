"""Configuração do simulador (12-factor, via variáveis de ambiente e .env)."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# simulator/config.py -> parents[0]=simulator, parents[1]=raiz do repositório.
PROJECT_ROOT = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Configurações do simulador, carregadas de variáveis de ambiente e .env."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- integração com o backend ---
    api_base_url: str = "http://127.0.0.1:8000"

    # --- ciclo de leitura ---
    sensor_interval_seconds: float = Field(default=10.0, gt=0.0)
    request_timeout_seconds: float = Field(default=5.0, gt=0.0)

    # --- modelo físico do sensor ultrassônico ---
    # Profundidade nominal do contêiner em cm (distância quando vazio).
    container_depth_cm: float = Field(default=100.0, gt=0.0)
    # Variação máxima de ocupação por "tick" (degrau do passeio aleatório).
    step_max: float = Field(default=3.0, gt=0.0, le=50.0)

    @property
    def readings_endpoint(self) -> str:
        """URL completa do endpoint de telemetria."""
        return f"{self.api_base_url.rstrip('/')}/api/v1/sensors/readings"


@dataclass(frozen=True, slots=True)
class SensorSpec:
    """Descrição estática de um sensor virtual."""

    sensor_id: str
    container_code: str
    initial_fill: float = 50.0
    min_fill: float = 0.0
    max_fill: float = 100.0


# Sensores padrão, alinhados aos contêineres criados pelo seed do backend
# (backend/app/db/seed.py). Cada sensor só envia leituras do seu contêiner.
DEFAULT_SENSOR_SPECS: tuple[SensorSpec, ...] = (
    SensorSpec("SENSOR-001", "CONT-001", initial_fill=35.0),
    SensorSpec("SENSOR-002", "CONT-002", initial_fill=72.0),
    SensorSpec("SENSOR-003", "CONT-003", initial_fill=83.0),
    SensorSpec("SENSOR-004", "CONT-004", initial_fill=95.0),
    SensorSpec("SENSOR-005", "CONT-005", initial_fill=88.0),
    SensorSpec("SENSOR-006", "CONT-006", initial_fill=60.0),
)


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância única de configuração do simulador."""
    return Settings()
