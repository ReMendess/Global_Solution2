"""Utilitário de data/hora: todo o sistema usa UTC sem timezone (SQLite)."""

from __future__ import annotations

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Data/hora atual em UTC, sem tzinfo, para gravação consistente no SQLite."""
    return datetime.now(UTC).replace(tzinfo=None)
