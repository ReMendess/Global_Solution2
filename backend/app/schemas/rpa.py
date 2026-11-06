"""Schemas das rotas de RPA (fila de demandas e execuções)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import OccurrenceCategory, OccurrenceStatus, Priority, RPAStatus


class RPAQueueItem(BaseModel):
    """Demanda elegível para encaminhamento ao portal administrativo."""

    occurrence_id: int
    protocol: str
    category: OccurrenceCategory
    priority: Priority
    status: OccurrenceStatus
    neighborhood: str
    address: str | None = None
    description: str | None = None


class RPAQueueList(BaseModel):
    """Fila de demandas pendentes de despacho."""

    total: int
    items: list[RPAQueueItem]


class RPAExecutionCreate(BaseModel):
    """Resultado de uma execução devolvido pelo robô à API."""

    occurrence_id: int
    status: RPAStatus
    portal_protocol: str | None = Field(default=None, max_length=60)
    duration_ms: int | None = Field(default=None, ge=0)
    error_message: str | None = Field(default=None, max_length=2000)
    screenshot_path: str | None = Field(default=None, max_length=255)


class RPAExecutionRead(BaseModel):
    """Registro persistido de uma execução do RPA."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    occurrence_id: int
    status: RPAStatus
    portal_protocol: str | None = None
    attempt: int
    error_message: str | None = None
    screenshot_path: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
    duration_ms: int | None = None


class RPAExecutionList(BaseModel):
    """Histórico paginado de execuções."""

    items: list[RPAExecutionRead]
    total: int
    limit: int
    offset: int
