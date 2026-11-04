"""Regras de negócio de ocorrências: registro, consulta e transição de status."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.clock import utcnow
from app.core.config import get_settings
from app.core.constants import (
    ALLOWED_TRANSITIONS,
    DISPATCHABLE_CATEGORIES,
    STATUSES_REQUIRING_NOTE,
)
from app.core.enums import ModelLabel, OccurrenceCategory, OccurrenceStatus, StatusChangedBy
from app.core.exceptions import ConflictError, NotFoundError, UnprocessableError
from app.models.occurrence import Occurrence, OccurrenceImage, StatusHistory
from app.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceDetail,
    OccurrenceList,
    OccurrenceRead,
    OccurrenceStatusUpdate,
)
from app.services import (
    classification_service,
    dedup_service,
    priority_service,
    protocol_service,
    storage_service,
)

if TYPE_CHECKING:
    from fastapi import UploadFile


def _record_history(
    occurrence: Occurrence,
    *,
    from_status: OccurrenceStatus | None,
    to_status: OccurrenceStatus,
    changed_by: StatusChangedBy,
    note: str | None = None,
) -> None:
    """Anexa um item à trilha de auditoria da ocorrência."""
    occurrence.status_history.append(
        StatusHistory(
            from_status=from_status.value if from_status else None,
            to_status=to_status.value,
            note=note,
            changed_by=changed_by.value,
        )
    )


def _transition(
    occurrence: Occurrence,
    target: OccurrenceStatus,
    *,
    changed_by: StatusChangedBy,
    note: str | None = None,
    reference: datetime | None = None,
) -> None:
    """Valida e aplica uma transição de status permitida."""
    atual = OccurrenceStatus(occurrence.status)
    if target not in ALLOWED_TRANSITIONS[atual]:
        raise ConflictError(f"Transição de {atual.value} para {target.value} não é permitida.")
    occurrence.status = target.value
    occurrence.updated_at = reference or utcnow()
    _record_history(
        occurrence,
        from_status=atual,
        to_status=target,
        changed_by=changed_by,
        note=note,
    )


def _resolve_category(
    model_label: str | None,
    confidence: float | None,
    reported_category: OccurrenceCategory,
) -> OccurrenceCategory:
    """Combina a categoria informada com o resultado do modelo.

    Sem modelo, prevalece a categoria informada pelo cidadão. Com modelo, uma imagem
    IRREGULAR confiável converte `OTHER` em `ILLEGAL_DUMPING` (descarte irregular genérico).
    """
    if model_label is None or confidence is None:
        return reported_category
    if (
        model_label == ModelLabel.IRREGULAR.value
        and confidence >= get_settings().confidence_threshold
        and reported_category == OccurrenceCategory.OTHER
    ):
        return OccurrenceCategory.ILLEGAL_DUMPING
    return reported_category


def create_occurrence(
    db: Session,
    data: OccurrenceCreate,
    image: UploadFile | None = None,
) -> OccurrenceDetail:
    """Registra uma ocorrência, grava a imagem e executa a etapa de classificação."""
    agora = utcnow()
    settings = get_settings()
    categoria_informada = OccurrenceCategory(data.reported_category or OccurrenceCategory.OTHER)

    dedup_hash = dedup_service.build_dedup_hash(
        neighborhood=data.neighborhood,
        category=categoria_informada.value,
        latitude=data.latitude,
        longitude=data.longitude,
        reference=agora,
    )
    duplicada = dedup_service.find_recent_duplicate(db, dedup_hash, agora)
    if duplicada is not None:
        raise ConflictError(
            "Já existe uma ocorrência aberta para este local hoje "
            f"(protocolo {duplicada.protocol})."
        )

    saved_image = storage_service.save_upload(image) if image is not None else None
    image_path = (
        settings.resolved_upload_dir / saved_image.file_path if saved_image is not None else None
    )
    classification = classification_service.classify_image(image_path)

    model_label = classification.label if classification else None
    confidence = classification.confidence if classification else None
    model_version = classification.model_version if classification else None

    categoria = _resolve_category(model_label, confidence, categoria_informada)
    prioridade, revisao = priority_service.resolve_priority(
        category=categoria,
        model_label=model_label,
        confidence=confidence,
    )

    occurrence = Occurrence(
        protocol=protocol_service.next_protocol(db),
        category=categoria.value,
        description=data.description,
        neighborhood=data.neighborhood.strip(),
        address=data.address,
        latitude=data.latitude,
        longitude=data.longitude,
        status=OccurrenceStatus.OPEN.value,
        priority=prioridade.value,
        model_label=model_label,
        confidence=confidence,
        needs_human_review=revisao,
        model_version=model_version,
        dedup_hash=dedup_hash,
        is_simulated=False,
        created_at=agora,
        updated_at=agora,
    )
    db.add(occurrence)
    db.flush()

    if saved_image is not None:
        db.add(
            OccurrenceImage(
                occurrence_id=occurrence.id,
                file_path=saved_image.file_path,
                content_type=saved_image.content_type,
                size_bytes=saved_image.size_bytes,
                width=saved_image.width,
                height=saved_image.height,
                is_simulated=False,
            )
        )

    _record_history(
        occurrence,
        from_status=None,
        to_status=OccurrenceStatus.OPEN,
        changed_by=StatusChangedBy.CITIZEN,
        note="Ocorrência registrada.",
    )

    if saved_image is not None:
        nota = (
            "Classificação executada pelo modelo."
            if classification is not None
            else "Modelo indisponível: classificação pendente de revisão humana."
        )
        _transition(
            occurrence,
            OccurrenceStatus.CLASSIFIED,
            changed_by=StatusChangedBy.SYSTEM,
            note=nota,
            reference=agora,
        )

    if categoria.value in DISPATCHABLE_CATEGORIES and not revisao:
        _transition(
            occurrence,
            OccurrenceStatus.PENDING_DISPATCH,
            changed_by=StatusChangedBy.SYSTEM,
            note="Ocorrência elegível para encaminhamento via RPA.",
            reference=agora,
        )

    db.commit()
    return get_detail(db, occurrence.id)


def _occurrence_query():
    """Consulta base com carregamento das relações usadas no detalhe."""
    return select(Occurrence).options(
        selectinload(Occurrence.images),
        selectinload(Occurrence.status_history),
    )


def get_detail(db: Session, occurrence_id: int) -> OccurrenceDetail:
    """Retorna o detalhe completo de uma ocorrência pelo id."""
    occurrence = db.execute(
        _occurrence_query().where(Occurrence.id == occurrence_id)
    ).scalar_one_or_none()
    if occurrence is None:
        raise NotFoundError(f"Ocorrência {occurrence_id} não encontrada.")
    return OccurrenceDetail.model_validate(occurrence)


def get_by_protocol(db: Session, protocol: str) -> OccurrenceRead:
    """Consulta pública pelo protocolo informado ao cidadão."""
    occurrence = db.execute(
        select(Occurrence).where(Occurrence.protocol == protocol.strip().upper())
    ).scalar_one_or_none()
    if occurrence is None:
        raise NotFoundError(f"Protocolo {protocol} não encontrado.")
    return OccurrenceRead.model_validate(occurrence)


def list_occurrences(
    db: Session,
    *,
    status: OccurrenceStatus | None = None,
    category: OccurrenceCategory | None = None,
    priority: str | None = None,
    neighborhood: str | None = None,
    needs_human_review: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> OccurrenceList:
    """Lista ocorrências com filtros e paginação (visão administrativa)."""
    filtros = []
    if status is not None:
        filtros.append(Occurrence.status == status.value)
    if category is not None:
        filtros.append(Occurrence.category == category.value)
    if priority is not None:
        filtros.append(Occurrence.priority == priority)
    if neighborhood:
        filtros.append(func.lower(Occurrence.neighborhood) == neighborhood.strip().lower())
    if needs_human_review is not None:
        filtros.append(Occurrence.needs_human_review.is_(needs_human_review))

    total = db.execute(
        select(func.count()).select_from(select(Occurrence.id).where(*filtros).subquery())
    ).scalar_one()

    ocorrencias = (
        db.execute(
            select(Occurrence)
            .where(*filtros)
            .order_by(Occurrence.created_at.desc(), Occurrence.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return OccurrenceList(
        items=[OccurrenceRead.model_validate(item) for item in ocorrencias],
        total=total,
        limit=limit,
        offset=offset,
    )


def change_status(
    db: Session,
    occurrence_id: int,
    update: OccurrenceStatusUpdate,
    *,
    changed_by: StatusChangedBy = StatusChangedBy.ADMIN,
) -> OccurrenceDetail:
    """Aplica uma transição de status solicitada pelo administrador."""
    occurrence = db.get(Occurrence, occurrence_id)
    if occurrence is None:
        raise NotFoundError(f"Ocorrência {occurrence_id} não encontrada.")

    if update.status in STATUSES_REQUIRING_NOTE and not (update.note or "").strip():
        raise UnprocessableError(
            f"A transição para {update.status.value} exige uma observação (note)."
        )

    _transition(
        occurrence,
        update.status,
        changed_by=changed_by,
        note=update.note,
    )
    db.commit()
    return get_detail(db, occurrence_id)
