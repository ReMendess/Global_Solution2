"""Modelo de usuário (perfis cidadão e administrador)."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.enums import UserRole
from app.db.base import Base

if TYPE_CHECKING:
    from app.models.occurrence import Occurrence


class User(Base):
    """Usuário do sistema. Guarda apenas o mínimo necessário (sem dados pessoais extras)."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.CITIZEN.value, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow, nullable=False)

    occurrences: Mapped[list[Occurrence]] = relationship(back_populates="user")

    def __repr__(self) -> str:  # pragma: no cover - apoio a depuração
        return f"<User id={self.id} email={self.email!r} role={self.role}>"
