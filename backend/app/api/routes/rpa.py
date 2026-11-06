"""Rotas do RPA: fila de demandas e histórico de execuções."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.db.session import get_db
from app.schemas.rpa import (
    RPAExecutionCreate,
    RPAExecutionList,
    RPAExecutionRead,
    RPAQueueList,
)
from app.services import rpa_service

router = APIRouter(prefix="/api/v1/rpa", tags=["rpa"])


@router.get("/queue", response_model=RPAQueueList, summary="Demandas elegíveis (PENDING_DISPATCH)")
def get_queue(db: Session = Depends(get_db)) -> RPAQueueList:
    """Fila consumida pelo robô; não expõe dados pessoais."""
    return rpa_service.list_queue(db)


@router.post(
    "/executions",
    response_model=RPAExecutionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registra o resultado de uma execução do RPA",
)
def create_execution(
    payload: RPAExecutionCreate,
    db: Session = Depends(get_db),
) -> RPAExecutionRead:
    """Persiste o sucesso/falha do preenchimento do portal e atualiza a ocorrência."""
    return rpa_service.record_execution(db, payload)


@router.get(
    "/executions",
    response_model=RPAExecutionList,
    summary="Histórico de execuções do RPA (administrativo)",
)
def list_executions(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> RPAExecutionList:
    """Histórico paginado, das execuções mais recentes para as mais antigas."""
    return rpa_service.list_executions(db, limit=limit, offset=offset)
