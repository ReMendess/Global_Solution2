"""Modelos de contêiner urbano e leituras de sensores (IoT simulado)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.enums import AlertLevel
from app.db.base import Base

if TYPE_CHECKING:
    pass


class Container(Base):
    """Contêiner urbano monitorado. Neste projeto todos são simulados."""

    __tablename__ = "containers"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    neighborhood: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    capacity_liters: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    current_fill_level: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    alert_level: Mapped[str] = mapped_column(
        String(20), default=AlertLevel.NORMAL.value, index=True, nullable=False
    )
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_reading_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    readings: Mapped[list[SensorReading]] = relationship(
        back_populates="container", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - apoio a depuração
        return f"<Container code={self.code!r} fill={self.current_fill_level}>"


class SensorReading(Base):
    """Leitura de um sensor ultrassônico virtual associado a um contêiner."""

    __tablename__ = "sensor_readings"

    id: Mapped[int] = mapped_column(primary_key=True)
    sensor_id: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    container_id: Mapped[int] = mapped_column(
        ForeignKey("containers.id"), index=True, nullable=False
    )
    fill_level: Mapped[float] = mapped_column(Float, nullable=False)
    distance_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    measured_at: Mapped[datetime] = mapped_column(DateTime, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    container: Mapped[Container] = relationship(back_populates="readings")
