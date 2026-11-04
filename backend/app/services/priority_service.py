"""Cálculo determinístico de prioridade e sinalização de revisão humana."""

from __future__ import annotations

from app.core.config import get_settings
from app.core.constants import PRIORITY_ORDER
from app.core.enums import ModelLabel, OccurrenceCategory, Priority

# Confiança mínima para tratar uma classificação IRREGULAR como prioridade alta.
HIGH_CONFIDENCE = 0.85


def raise_priority(priority: Priority, levels: int = 1) -> Priority:
    """Sobe a prioridade em `levels` degraus, sem ultrapassar CRITICAL."""
    indice = PRIORITY_ORDER.index(priority) + levels
    return PRIORITY_ORDER[min(indice, len(PRIORITY_ORDER) - 1)]


def resolve_priority(
    *,
    category: OccurrenceCategory | str,
    model_label: str | None,
    confidence: float | None,
) -> tuple[Priority, bool]:
    """Define prioridade e necessidade de revisão humana.

    Retorna (prioridade, needs_human_review). Regras em docs/BUSINESS_RULES.md §4.
    """
    threshold = get_settings().confidence_threshold
    categoria = OccurrenceCategory(category)
    revisao = False

    if model_label is None or confidence is None:
        # Modelo indisponível (FASE 1) ou falha de inferência: registro segue normalmente.
        prioridade = Priority.MEDIUM
        revisao = True
    elif model_label == ModelLabel.IRREGULAR.value:
        prioridade = Priority.HIGH if confidence >= HIGH_CONFIDENCE else Priority.MEDIUM
        revisao = confidence < threshold
    else:
        prioridade = Priority.LOW
        revisao = confidence < threshold

    if (
        categoria == OccurrenceCategory.OVERFLOW
        or categoria == OccurrenceCategory.DAMAGED_CONTAINER
    ):
        prioridade = raise_priority(prioridade)
    elif categoria == OccurrenceCategory.OTHER:
        revisao = True

    return prioridade, revisao
