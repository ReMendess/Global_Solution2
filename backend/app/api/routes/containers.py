"""Rotas de contêineres urbanos."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.enums import AlertLevel
from app.db.session import get_db
from app.schemas.container import ContainerList, ContainerRead, SensorReadingList
from app.services import container_service

router = APIRouter(prefix="/api/v1/containers", tags=["contêineres"])


@router.get("", response_model=ContainerList, summary="Lista contêineres (administrativo)")
def list_containers(
    neighborhood: Annotated[str | None, Query(max_length=120)] = None,
    alert_level: Annotated[AlertLevel | None, Query()] = None,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> ContainerList:
    """Lista os contêineres com o nível de ocupação atual."""
    return container_service.list_containers(db, neighborhood=neighborhood, alert_level=alert_level)


@router.get("/{code}", response_model=ContainerRead, summary="Detalhe de um contêiner pelo código")
def get_container(code: str, db: Session = Depends(get_db)) -> ContainerRead:
    """Consulta pública do estado de um contêiner."""
    return container_service.get_container(db, code)


@router.get(
    "/{code}/readings",
    response_model=SensorReadingList,
    summary="Histórico de leituras de um contêiner (administrativo)",
)
def list_readings(
    code: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> SensorReadingList:
    """Histórico paginado, das leituras mais recentes para as mais antigas."""
    return container_service.list_readings(db, code, limit=limit, offset=offset)
