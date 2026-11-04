"""Modelos de automação: execuções do RPA e interações do agente."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.enums import RPAStatus
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.occurrence import Occurrence


class RPAExecution(Base):
    """Registro de cada tentativa de encaminhamento de uma ocorrência ao portal."""

    __tablename__ = "rpa_executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    occurrence_id: Mapped[int] = mapped_column(
        ForeignKey("occurrences.id"), index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=RPAStatus.FAILED.value, index=True, nullable=False
    )
    portal_protocol: Mapped[str | None] = mapped_column(String(60), nullable=True)
    attempt: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    screenshot_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    occurrence: Mapped[Occurrence] = relationship(back_populates="rpa_executions")


class AgentInteraction(Base):
    """Histórico de conversas com o agente (contexto e ferramenta utilizada)."""

    __tablename__ = "agent_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    intent: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    tool_used: Mapped[str | None] = mapped_column(String(60), nullable=True)
    tool_payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=utcnow, index=True, nullable=False
    )
