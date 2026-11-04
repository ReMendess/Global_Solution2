"""Enums canônicos do domínio (fonte única para API, banco e frontend)."""

from __future__ import annotations

from enum import StrEnum


class OccurrenceCategory(StrEnum):
    """Categorias de ocorrência previstas no desafio."""

    ILLEGAL_DUMPING = "ILLEGAL_DUMPING"
    OVERFLOW = "OVERFLOW"
    DAMAGED_CONTAINER = "DAMAGED_CONTAINER"
    OTHER = "OTHER"


class ModelLabel(StrEnum):
    """Classes previstas para o modelo de visão computacional."""

    REGULAR = "REGULAR"
    IRREGULAR = "IRREGULAR"


class OccurrenceStatus(StrEnum):
    """Estados do ciclo de vida de uma ocorrência."""

    OPEN = "OPEN"
    CLASSIFIED = "CLASSIFIED"
    PENDING_DISPATCH = "PENDING_DISPATCH"
    DISPATCHED = "DISPATCHED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"


class Priority(StrEnum):
    """Prioridade calculada pelo backend."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertLevel(StrEnum):
    """Nível de alerta de ocupação de contêiner."""

    NORMAL = "NORMAL"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(StrEnum):
    """Perfis de acesso previstos no desafio."""

    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"


class RPAStatus(StrEnum):
    """Resultado de uma execução de automação."""

    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class StatusChangedBy(StrEnum):
    """Origem de uma transição de status (auditoria)."""

    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"
    RPA = "RPA"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"
