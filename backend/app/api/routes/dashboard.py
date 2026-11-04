"""Rotas dos indicadores do dashboard administrativo."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.dashboard import (
    ContainerAlertSummary,
    DashboardSummary,
    NeighborhoodRanking,
)
from app.services import dashboard_service

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Totais por status, categoria e prioridade",
)
def get_summary(
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> DashboardSummary:
    """Indicadores gerais calculados diretamente dos dados persistidos."""
    return dashboard_service.summary(db)


@router.get(
    "/containers",
    response_model=ContainerAlertSummary,
    summary="Contêineres por nível de alerta",
)
def get_container_alerts(
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> ContainerAlertSummary:
    """Distribuição dos contêineres e destaque dos que estão em nível crítico."""
    return dashboard_service.container_alerts(db)


@router.get(
    "/neighborhoods",
    response_model=NeighborhoodRanking,
    summary="Ranking de bairros com mais ocorrências",
)
def get_neighborhood_ranking(
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> NeighborhoodRanking:
    """Ranking decrescente por volume de ocorrências."""
    return dashboard_service.neighborhood_ranking(db, limit=limit)
