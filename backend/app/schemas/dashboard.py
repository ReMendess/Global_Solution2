"""Schemas dos indicadores exibidos no dashboard administrativo."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.core.enums import AlertLevel


class DashboardSummary(BaseModel):
    """Resumo geral das ocorrências persistidas."""

    total_occurrences: int
    by_status: dict[str, int] = Field(default_factory=dict)
    by_category: dict[str, int] = Field(default_factory=dict)
    by_priority: dict[str, int] = Field(default_factory=dict)
    needs_human_review: int = 0
    average_resolution_hours: float | None = None


class ContainerAlertSummary(BaseModel):
    """Distribuição dos contêineres por nível de alerta."""

    total_containers: int
    by_alert_level: dict[str, int] = Field(default_factory=dict)
    critical_codes: list[str] = Field(default_factory=list)


class NeighborhoodItem(BaseModel):
    """Total de ocorrências por bairro."""

    neighborhood: str
    total: int


class NeighborhoodRanking(BaseModel):
    """Ranking de bairros com mais ocorrências."""

    items: list[NeighborhoodItem]
    limit: int


__all__ = [
    "AlertLevel",
    "ContainerAlertSummary",
    "DashboardSummary",
    "NeighborhoodItem",
    "NeighborhoodRanking",
]
