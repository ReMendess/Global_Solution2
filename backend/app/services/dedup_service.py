"""Deduplicação de ocorrências (evita registros repetidos no mesmo local/dia)."""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    DEDUP_COORDINATE_PRECISION,
    DEDUP_WINDOW_HOURS,
    TERMINAL_STATUSES,
)
from app.models.occurrence import Occurrence


def _format_coordinate(value: float | None) -> str:
    """Normaliza a coordenada para reduzir variações mínimas de GPS."""
    if value is None:
        return ""
    return f"{round(value, DEDUP_COORDINATE_PRECISION):.{DEDUP_COORDINATE_PRECISION}f}"


def build_dedup_hash(
    *,
    neighborhood: str,
    category: str,
    latitude: float | None,
    longitude: float | None,
    reference: datetime,
) -> str:
    """Gera o hash de deduplicação da ocorrência (ver DATA_MODEL.md §5)."""
    partes = [
        neighborhood.strip().lower(),
        category,
        _format_coordinate(latitude),
        _format_coordinate(longitude),
        reference.strftime("%Y-%m-%d"),
    ]
    return hashlib.sha256("|".join(partes).encode("utf-8")).hexdigest()


def find_recent_duplicate(db: Session, dedup_hash: str, reference: datetime) -> Occurrence | None:
    """Busca ocorrência aberta com o mesmo hash dentro da janela de deduplicação."""
    inicio = reference - timedelta(hours=DEDUP_WINDOW_HOURS)
    stmt = (
        select(Occurrence)
        .where(
            Occurrence.dedup_hash == dedup_hash,
            Occurrence.created_at >= inicio,
            Occurrence.status.notin_([status.value for status in TERMINAL_STATUSES]),
        )
        .order_by(Occurrence.created_at.desc())
        .limit(1)
    )
    return db.execute(stmt).scalar_one_or_none()
