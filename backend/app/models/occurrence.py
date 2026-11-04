"""Modelos de ocorrência, suas imagens e o histórico de status."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.enums import OccurrenceCategory, OccurrenceStatus, Priority, StatusChangedBy
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.automation import RPAExecution
    from app.models.user import User


class Occurrence(Base):
    """Ocorrência registrada pelo cidadão (com classificação e status rastreados)."""

    __tablename__ = "occurrences"

    id: Mapped[int] = mapped_column(primary_key=True)
    protocol: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    category: Mapped[str] = mapped_column(
        String(30), default=OccurrenceCategory.OTHER.value, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    neighborhood: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[str] = mapped_column(
        String(30), default=OccurrenceStatus.OPEN.value, index=True, nullable=False
    )
    priority: Mapped[str] = mapped_column(
        String(20), default=Priority.MEDIUM.value, index=True, nullable=False
    )

    model_label: Mapped[str | None] = mapped_column(String(20), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    needs_human_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(60), nullable=True)

    dispatch_protocol: Mapped[str | None] = mapped_column(String(60), nullable=True)
    dedup_hash: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, index=True, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, onupdate=utcnow, nullable=False
    )

    user: Mapped[User | None] = relationship(back_populates="occurrences")
    images: Mapped[list[OccurrenceImage]] = relationship(
        back_populates="occurrence", cascade="all, delete-orphan"
    )
    status_history: Mapped[list[StatusHistory]] = relationship(
        back_populates="occurrence",
        cascade="all, delete-orphan",
        order_by="StatusHistory.id",
    )
    rpa_executions: Mapped[list[RPAExecution]] = relationship(
        back_populates="occurrence", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - apoio a depuração
        return f"<Occurrence id={self.id} protocol={self.protocol!r} status={self.status}>"


class OccurrenceImage(Base):
    """Imagem enviada pelo cidadão; o arquivo fica em disco (ADR-005)."""

    __tablename__ = "occurrence_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(
        ForeignKey("occurrences.id"), index=True, nullable=False
    )
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(60), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    occurrence: Mapped[Occurrence] = relationship(back_populates="images")


class StatusHistory(Base):
    """Trilha de auditoria de toda transição de status de uma ocorrência."""

    __tablename__ = "status_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(
        ForeignKey("occurrences.id"), index=True, nullable=False
    )
    from_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    changed_by: Mapped[str] = mapped_column(
        String(30), default=StatusChangedBy.SYSTEM.value, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, index=True, nullable=False
    )

    occurrence: Mapped[Occurrence] = relationship(back_populates="status_history")
