"""Base declarativa do SQLAlchemy 2.0."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base de todos os modelos ORM do projeto."""
