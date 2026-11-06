"""Regras de negócio do RPA: fila de demandas e registro de execuções.

O robô (rpa/bot) consulta as demandas elegíveis, preenche o portal administrativo
fictício e devolve o resultado para cá. Cada ocorrência só pode ter uma execução
`SUCCESS` (controle contra duplicidade — docs/BUSINESS_RULES.md §7).
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.constants import ALLOWED_TRANSITIONS, PRIORITY_ORDER
from app.core.enums import (
    OccurrenceStatus,
    Priority,
    RPAStatus,
    StatusChangedBy,
)
from app.core.exceptions import ConflictError, NotFoundError
from app.models.automation import RPAExecution
from app.models.occurrence import Occurrence, StatusHistory
from app.schemas.rpa import (
    RPAExecutionCreate,
    RPAExecutionList,
    RPAExecutionRead,
    RPAQueueItem,
    RPAQueueList,
)


def _occurrence_em_pending(db: Session, occurrence_id: int) -> Occurrence:
    """Busca a ocorrência ou levanta 404; não valida o status aqui."""
    occurrence = db.get(Occurrence, occurrence_id)
    if occurrence is None:
        raise NotFoundError(f"Ocorrência {occurrence_id} não encontrada.")
    return occurrence


def _assert_pending(occurrence: Occurrence) -> None:
    """Garante o status PENDING_DISPATCH para o despacho."""
    if occurrence.status != OccurrenceStatus.PENDING_DISPATCH.value:
        raise ConflictError(
            f"Ocorrência {occurrence.id} não está em PENDING_DISPATCH (status atual: "
            f"{occurrence.status})."
        )


def _has_success(db: Session, occurrence_id: int) -> bool:
    """Verifica se já existe uma execução bem-sucedida para a ocorrência."""
    existe = db.execute(
        select(RPAExecution.id).where(
            RPAExecution.occurrence_id == occurrence_id,
            RPAExecution.status == RPAStatus.SUCCESS.value,
        )
    ).scalar_one_or_none()
    return existe is not None


def _sort_key(item: Occurrence) -> tuple[int, str]:
    """Ordena por prioridade (maior primeiro) e depois por ordem de criação."""
    prioridade = Priority(item.priority)
    indice = PRIORITY_ORDER.index(prioridade)
    return (-indice, item.created_at.isoformat())


def list_queue(db: Session) -> RPAQueueList:
    """Lista as demandas elegíveis (`PENDING_DISPATCH`) em ordem de prioridade."""
    ocorrencias = (
        db.execute(
            select(Occurrence)
            .where(Occurrence.status == OccurrenceStatus.PENDING_DISPATCH.value)
            .order_by(Occurrence.created_at.asc())
        )
        .scalars()
        .all()
    )

    ordenadas = sorted(ocorrencias, key=_sort_key)
    items = [
        RPAQueueItem(
            occurrence_id=item.id,
            protocol=item.protocol,
            category=item.category,
            priority=item.priority,
            status=item.status,
            neighborhood=item.neighborhood,
            address=item.address,
            description=item.description,
        )
        for item in ordenadas
    ]
    return RPAQueueList(total=len(items), items=items)


def next_attempt(db: Session, occurrence_id: int) -> int:
    """Quantidade de tentativas já registradas + 1."""
    ultima = db.execute(
        select(func.max(RPAExecution.attempt)).where(RPAExecution.occurrence_id == occurrence_id)
    ).scalar_one_or_none()
    return (ultima or 0) + 1


def record_execution(db: Session, payload: RPAExecutionCreate) -> RPAExecutionRead:
    """Registra o resultado de uma execução do RPA.

    - `SUCCESS`: a ocorrência vai para `DISPATCHED` e grava `dispatch_protocol`.
    - `FAILED`/`SKIPPED`: a ocorrência permanece `PENDING_DISPATCH`.
    - Segunda execução `SUCCESS` para a mesma ocorrência → `409`.
    """
    occurrence = _occurrence_em_pending(db, payload.occurrence_id)

    if payload.status == RPAStatus.SUCCESS:
        if not payload.portal_protocol:
            raise ConflictError("Execução SUCCESS exige o portal_protocol capturado.")
        if _has_success(db, payload.occurrence_id):
            raise ConflictError(
                f"Ocorrência {payload.occurrence_id} já foi despachada com sucesso."
            )

    _assert_pending(occurrence)

    agora = utcnow()
    execucao = RPAExecution(
        occurrence_id=payload.occurrence_id,
        status=payload.status.value,
        portal_protocol=payload.portal_protocol,
        attempt=next_attempt(db, payload.occurrence_id),
        error_message=payload.error_message,
        screenshot_path=payload.screenshot_path,
        started_at=agora,
        finished_at=agora,
        duration_ms=payload.duration_ms,
    )
    db.add(execucao)

    if payload.status == RPAStatus.SUCCESS:
        # Transição PENDING_DISPATCH -> DISPATCHED, registrada na auditoria.
        if (
            OccurrenceStatus.DISPATCHED
            not in ALLOWED_TRANSITIONS[OccurrenceStatus(occurrence.status)]
        ):
            raise ConflictError("Transição para DISPATCHED não é permitida no estado atual.")
        occurrence.status = OccurrenceStatus.DISPATCHED.value
        occurrence.dispatch_protocol = payload.portal_protocol
        occurrence.updated_at = agora
        occurrence.status_history.append(
            StatusHistory(
                from_status=OccurrenceStatus.PENDING_DISPATCH.value,
                to_status=OccurrenceStatus.DISPATCHED.value,
                note=f"Despachado pelo RPA (protocolo do portal: {payload.portal_protocol}).",
                changed_by=StatusChangedBy.RPA.value,
                created_at=agora,
            )
        )

    db.commit()
    db.refresh(execucao)
    return RPAExecutionRead.model_validate(execucao)


def list_executions(db: Session, *, limit: int = 20, offset: int = 0) -> RPAExecutionList:
    """Histórico paginado de execuções do RPA (mais recentes primeiro)."""
    total = db.execute(select(func.count()).select_from(RPAExecution)).scalar_one()
    execucoes = (
        db.execute(
            select(RPAExecution)
            .order_by(RPAExecution.started_at.desc(), RPAExecution.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )
    return RPAExecutionList(
        items=[RPAExecutionRead.model_validate(item) for item in execucoes],
        total=total,
        limit=limit,
        offset=offset,
    )
