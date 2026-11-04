"""Cálculo dos indicadores do dashboard administrativo."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import AlertLevel, OccurrenceStatus
from app.models.container import Container
from app.models.occurrence import Occurrence
from app.schemas.dashboard import (
    ContainerAlertSummary,
    DashboardSummary,
    NeighborhoodItem,
    NeighborhoodRanking,
)


def _count_by(db: Session, column) -> dict[str, int]:
    """Agrupa a contagem de ocorrências por uma coluna."""
    linhas = db.execute(select(column, func.count(Occurrence.id)).group_by(column)).all()
    return {str(valor): int(total) for valor, total in linhas}


def summary(db: Session) -> DashboardSummary:
    """Resumo geral: totais por status, categoria e prioridade, e tempo médio de resolução."""
    total = db.execute(select(func.count()).select_from(Occurrence)).scalar_one()
    revisao = db.execute(
        select(func.count()).select_from(Occurrence).where(Occurrence.needs_human_review.is_(True))
    ).scalar_one()

    resolvidas = db.execute(
        select(Occurrence.created_at, Occurrence.updated_at).where(
            Occurrence.status == OccurrenceStatus.RESOLVED.value
        )
    ).all()

    media_horas: float | None = None
    if resolvidas:
        duracoes = [
            (fim - inicio).total_seconds() / 3600 for inicio, fim in resolvidas if fim and inicio
        ]
        if duracoes:
            media_horas = round(sum(duracoes) / len(duracoes), 2)

    return DashboardSummary(
        total_occurrences=total,
        by_status=_count_by(db, Occurrence.status),
        by_category=_count_by(db, Occurrence.category),
        by_priority=_count_by(db, Occurrence.priority),
        needs_human_review=revisao,
        average_resolution_hours=media_horas,
    )


def container_alerts(db: Session) -> ContainerAlertSummary:
    """Distribuição dos contêineres por nível de alerta."""
    linhas = db.execute(
        select(Container.alert_level, func.count(Container.id)).group_by(Container.alert_level)
    ).all()
    por_nivel = {str(nivel): int(total) for nivel, total in linhas}

    criticos = (
        db.execute(
            select(Container.code)
            .where(Container.alert_level == AlertLevel.CRITICAL.value)
            .order_by(Container.code)
        )
        .scalars()
        .all()
    )

    return ContainerAlertSummary(
        total_containers=sum(por_nivel.values()),
        by_alert_level=por_nivel,
        critical_codes=list(criticos),
    )


def neighborhood_ranking(db: Session, limit: int = 10) -> NeighborhoodRanking:
    """Ranking de bairros com mais ocorrências registradas."""
    linhas = db.execute(
        select(Occurrence.neighborhood, func.count(Occurrence.id).label("total"))
        .group_by(Occurrence.neighborhood)
        .order_by(func.count(Occurrence.id).desc(), Occurrence.neighborhood)
        .limit(limit)
    ).all()

    return NeighborhoodRanking(
        items=[NeighborhoodItem(neighborhood=bairro, total=int(total)) for bairro, total in linhas],
        limit=limit,
    )
