"""Constantes de regra de negócio (limiares, transições, prioridades)."""

from __future__ import annotations

from app.core.enums import OccurrenceStatus, Priority

# --- Alertas de ocupação (PROJECT_CONTEXT.md §6) ---
# menor que 80% -> NORMAL | 80% a 89% -> HIGH | 90% ou mais -> CRITICAL
ALERT_HIGH_THRESHOLD = 80.0
ALERT_CRITICAL_THRESHOLD = 90.0

# --- Protocolo público da ocorrência ---
PROTOCOL_PREFIX = "CL"
PROTOCOL_SEQUENCE_DIGITS = 6

# --- Deduplicação de ocorrências ---
DEDUP_WINDOW_HOURS = 24
DEDUP_COORDINATE_PRECISION = 4

# --- Prioridades ---
PRIORITY_ORDER: tuple[Priority, ...] = (
    Priority.LOW,
    Priority.MEDIUM,
    Priority.HIGH,
    Priority.CRITICAL,
)

# --- Máquina de estados da ocorrência ---
ALLOWED_TRANSITIONS: dict[OccurrenceStatus, frozenset[OccurrenceStatus]] = {
    OccurrenceStatus.OPEN: frozenset(
        {
            OccurrenceStatus.CLASSIFIED,
            OccurrenceStatus.PENDING_DISPATCH,
            OccurrenceStatus.REJECTED,
        }
    ),
    OccurrenceStatus.CLASSIFIED: frozenset(
        {OccurrenceStatus.PENDING_DISPATCH, OccurrenceStatus.REJECTED}
    ),
    OccurrenceStatus.PENDING_DISPATCH: frozenset(
        {OccurrenceStatus.DISPATCHED, OccurrenceStatus.REJECTED}
    ),
    OccurrenceStatus.DISPATCHED: frozenset(
        {OccurrenceStatus.IN_PROGRESS, OccurrenceStatus.RESOLVED, OccurrenceStatus.REJECTED}
    ),
    OccurrenceStatus.IN_PROGRESS: frozenset({OccurrenceStatus.RESOLVED, OccurrenceStatus.REJECTED}),
    OccurrenceStatus.RESOLVED: frozenset(),
    OccurrenceStatus.REJECTED: frozenset(),
}

# Estados que exigem justificativa ao serem aplicados.
STATUSES_REQUIRING_NOTE = frozenset({OccurrenceStatus.RESOLVED, OccurrenceStatus.REJECTED})

# Estados terminais: não voltam para a fila do RPA.
TERMINAL_STATUSES = frozenset({OccurrenceStatus.RESOLVED, OccurrenceStatus.REJECTED})

# Categorias que podem ser encaminhadas ao portal via RPA.
DISPATCHABLE_CATEGORIES = frozenset(
    {
        "ILLEGAL_DUMPING",
        "OVERFLOW",
        "DAMAGED_CONTAINER",
    }
)

# --- Upload de imagem ---
ALLOWED_IMAGE_TYPES: dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
}
