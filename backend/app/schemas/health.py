"""Schema de verificação de saúde da API."""

from __future__ import annotations

from pydantic import BaseModel


class HealthRead(BaseModel):
    """Resposta de /health."""

    status: str
    version: str
    environment: str
    database: str
    model_loaded: bool
