"""Rota de metadados: valores canônicos dos enums para o frontend."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.constants import ALLOWED_TRANSITIONS
from app.core.enums import (
    AlertLevel,
    ModelLabel,
    OccurrenceCategory,
    OccurrenceStatus,
    Priority,
    RPAStatus,
    UserRole,
)
from app.schemas.meta import EnumsRead

router = APIRouter(prefix="/api/v1/meta", tags=["metadados"])


@router.get("/enums", response_model=EnumsRead, summary="Valores canônicos do domínio")
def read_enums() -> EnumsRead:
    """Retorna todos os enums do sistema, evitando duplicação de valores no frontend."""
    return EnumsRead(
        categories=[item.value for item in OccurrenceCategory],
        model_labels=[item.value for item in ModelLabel],
        statuses=[item.value for item in OccurrenceStatus],
        priorities=[item.value for item in Priority],
        alert_levels=[item.value for item in AlertLevel],
        user_roles=[item.value for item in UserRole],
        rpa_statuses=[item.value for item in RPAStatus],
        allowed_transitions={
            origem.value: sorted(destino.value for destino in destinos)
            for origem, destinos in ALLOWED_TRANSITIONS.items()
        },
    )
