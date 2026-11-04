"""Rotas de ocorrências: registro pelo cidadão e gestão administrativa."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.enums import OccurrenceCategory, OccurrenceStatus, Priority, StatusChangedBy
from app.db.session import get_db
from app.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceDetail,
    OccurrenceList,
    OccurrenceRead,
    OccurrenceStatusUpdate,
)
from app.services import occurrence_service

router = APIRouter(prefix="/api/v1/occurrences", tags=["ocorrências"])


@router.post(
    "",
    response_model=OccurrenceDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Registra uma ocorrência com foto opcional",
)
def create_occurrence(
    neighborhood: Annotated[str, Form(min_length=3, max_length=120)],
    address: Annotated[str | None, Form(max_length=255)] = None,
    latitude: Annotated[float | None, Form(ge=-90, le=90)] = None,
    longitude: Annotated[float | None, Form(ge=-180, le=180)] = None,
    description: Annotated[str | None, Form(max_length=1000)] = None,
    reporter_name: Annotated[str | None, Form(max_length=120)] = None,
    reported_category: Annotated[OccurrenceCategory | None, Form()] = None,
    image: Annotated[UploadFile | None, File()] = None,
    db: Session = Depends(get_db),
) -> OccurrenceDetail:
    """Cria a ocorrência, grava a imagem e tenta classificá-la.

    O protocolo é devolvido na resposta; a classificação nunca impede o registro.
    """
    dados = OccurrenceCreate(
        neighborhood=neighborhood,
        address=address,
        latitude=latitude,
        longitude=longitude,
        description=description,
        reporter_name=reporter_name,
        reported_category=reported_category,
    )
    return occurrence_service.create_occurrence(db, dados, image)


@router.get(
    "/protocol/{protocol}",
    response_model=OccurrenceRead,
    summary="Consulta pública pelo protocolo",
)
def get_by_protocol(protocol: str, db: Session = Depends(get_db)) -> OccurrenceRead:
    """Permite ao cidadão acompanhar o status a partir do protocolo recebido."""
    return occurrence_service.get_by_protocol(db, protocol)


@router.get("", response_model=OccurrenceList, summary="Lista ocorrências (administrativo)")
def list_occurrences(
    status_filter: Annotated[OccurrenceStatus | None, Query(alias="status")] = None,
    category: Annotated[OccurrenceCategory | None, Query()] = None,
    priority: Annotated[Priority | None, Query()] = None,
    neighborhood: Annotated[str | None, Query(max_length=120)] = None,
    needs_human_review: Annotated[bool | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> OccurrenceList:
    """Lista paginada com filtros por status, categoria, prioridade e bairro."""
    return occurrence_service.list_occurrences(
        db,
        status=status_filter,
        category=category,
        priority=priority.value if priority else None,
        neighborhood=neighborhood,
        needs_human_review=needs_human_review,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{occurrence_id}",
    response_model=OccurrenceDetail,
    summary="Detalhe de uma ocorrência (administrativo)",
)
def get_occurrence(
    occurrence_id: int,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> OccurrenceDetail:
    """Retorna a ocorrência com imagens e histórico de status."""
    return occurrence_service.get_detail(db, occurrence_id)


@router.patch(
    "/{occurrence_id}/status",
    response_model=OccurrenceDetail,
    summary="Altera o status de uma ocorrência (administrativo)",
)
def update_status(
    occurrence_id: int,
    payload: OccurrenceStatusUpdate,
    _: Annotated[object, Depends(require_admin)] = None,
    db: Session = Depends(get_db),
) -> OccurrenceDetail:
    """Valida a transição na máquina de estados e registra a auditoria."""
    return occurrence_service.change_status(
        db,
        occurrence_id,
        payload,
        changed_by=StatusChangedBy.ADMIN,
    )
