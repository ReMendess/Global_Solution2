"""Geração do protocolo público das ocorrências (formato CL-AAAA-NNNNNN)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.constants import PROTOCOL_PREFIX, PROTOCOL_SEQUENCE_DIGITS
from app.models.occurrence import Occurrence


def protocol_prefix(year: int | None = None) -> str:
    """Prefixo do protocolo para o ano informado (padrão: ano atual)."""
    return f"{PROTOCOL_PREFIX}-{year or utcnow().year}-"


def next_protocol(db: Session, year: int | None = None) -> str:
    """Calcula o próximo protocolo sequencial do ano a partir do banco."""
    prefix = protocol_prefix(year)
    ultimo = db.execute(
        select(Occurrence.protocol)
        .where(Occurrence.protocol.like(f"{prefix}%"))
        .order_by(Occurrence.protocol.desc())
        .limit(1)
    ).scalar_one_or_none()

    sequencial = 1
    if ultimo:
        try:
            sequencial = int(ultimo.rsplit("-", 1)[-1]) + 1
        except ValueError:  # pragma: no cover - protocolo fora do padrão
            sequencial = 1

    return f"{prefix}{sequencial:0{PROTOCOL_SEQUENCE_DIGITS}d}"
