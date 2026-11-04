"""Schemas de contêiner e de leituras de sensores."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import AlertLevel


class ContainerRead(BaseModel):
    """Estado atual de um contêiner monitorado."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    neighborhood: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    capacity_liters: int
    current_fill_level: float
    alert_level: AlertLevel
    is_simulated: bool
    last_reading_at: datetime | None = None
    created_at: datetime


class ContainerList(BaseModel):
    """Lista de contêineres."""

    items: list[ContainerRead]
    total: int


class SensorReadingCreate(BaseModel):
    """Telemetria enviada por um sensor virtual (FASE 4 gera estes dados)."""

    sensor_id: str = Field(min_length=3, max_length=40)
    container_code: str = Field(min_length=3, max_length=40)
    fill_level: float = Field(ge=0.0, le=100.0)
    distance_cm: float | None = Field(default=None, ge=0.0)
    measured_at: datetime | None = None


class SensorReadingRead(BaseModel):
    """Leitura persistida de um sensor."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    sensor_id: str
    container_code: str
    fill_level: float
    distance_cm: float | None = None
    alert_level: AlertLevel
    is_simulated: bool
    measured_at: datetime
    created_at: datetime


class SensorReadingList(BaseModel):
    """Histórico paginado de leituras de um contêiner."""

    items: list[SensorReadingRead]
    total: int
    limit: int
    offset: int
