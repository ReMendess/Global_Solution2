"""Regras de contêineres urbanos e ingestão de telemetria dos sensores."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.constants import ALERT_CRITICAL_THRESHOLD, ALERT_HIGH_THRESHOLD
from app.core.enums import AlertLevel
from app.core.exceptions import NotFoundError, UnprocessableError
from app.models.container import Container, SensorReading
from app.schemas.container import (
    ContainerList,
    ContainerRead,
    SensorReadingCreate,
    SensorReadingList,
    SensorReadingRead,
)


def resolve_alert_level(fill_level: float) -> AlertLevel:
    """Aplica os limiares de ocupação definidos no desafio (80% e 90%)."""
    if fill_level >= ALERT_CRITICAL_THRESHOLD:
        return AlertLevel.CRITICAL
    if fill_level >= ALERT_HIGH_THRESHOLD:
        return AlertLevel.HIGH
    return AlertLevel.NORMAL


def _get_container_or_404(db: Session, code: str) -> Container:
    """Busca o contêiner pelo código ou levanta 404."""
    container = db.execute(
        select(Container).where(func.upper(Container.code) == code.strip().upper())
    ).scalar_one_or_none()
    if container is None:
        raise NotFoundError(f"Contêiner {code} não encontrado.")
    return container


def _to_reading_read(reading: SensorReading, container_code: str) -> SensorReadingRead:
    """Converte a leitura ORM para o schema público (inclui o código do contêiner)."""
    return SensorReadingRead(
        id=reading.id,
        sensor_id=reading.sensor_id,
        container_code=container_code,
        fill_level=reading.fill_level,
        distance_cm=reading.distance_cm,
        alert_level=AlertLevel(reading.alert_level),
        is_simulated=reading.is_simulated,
        measured_at=reading.measured_at,
        created_at=reading.created_at,
    )


def list_containers(
    db: Session,
    *,
    neighborhood: str | None = None,
    alert_level: AlertLevel | None = None,
) -> ContainerList:
    """Lista os contêineres monitorados, opcionalmente filtrados."""
    filtros = []
    if neighborhood:
        filtros.append(func.lower(Container.neighborhood) == neighborhood.strip().lower())
    if alert_level is not None:
        filtros.append(Container.alert_level == alert_level.value)

    containers = (
        db.execute(select(Container).where(*filtros).order_by(Container.code)).scalars().all()
    )
    return ContainerList(
        items=[ContainerRead.model_validate(item) for item in containers],
        total=len(containers),
    )


def get_container(db: Session, code: str) -> ContainerRead:
    """Detalhe de um contêiner pelo código."""
    return ContainerRead.model_validate(_get_container_or_404(db, code))


def register_reading(db: Session, payload: SensorReadingCreate) -> SensorReadingRead:
    """Persiste uma leitura de sensor e atualiza o estado do contêiner."""
    container = _get_container_or_404(db, payload.container_code)
    alerta = resolve_alert_level(payload.fill_level)
    agora = payload.measured_at or utcnow()

    reading = SensorReading(
        sensor_id=payload.sensor_id.strip(),
        container_id=container.id,
        fill_level=payload.fill_level,
        distance_cm=payload.distance_cm,
        alert_level=alerta.value,
        is_simulated=True,
        measured_at=agora,
    )
    db.add(reading)

    container.current_fill_level = payload.fill_level
    container.alert_level = alerta.value
    container.last_reading_at = agora

    db.commit()
    db.refresh(reading)
    return _to_reading_read(reading, container.code)


def list_readings(db: Session, code: str, *, limit: int = 20, offset: int = 0) -> SensorReadingList:
    """Histórico paginado de leituras de um contêiner (mais recentes primeiro)."""
    container = _get_container_or_404(db, code)

    total = db.execute(
        select(func.count())
        .select_from(SensorReading)
        .where(SensorReading.container_id == container.id)
    ).scalar_one()

    readings = (
        db.execute(
            select(SensorReading)
            .where(SensorReading.container_id == container.id)
            .order_by(SensorReading.measured_at.desc(), SensorReading.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return SensorReadingList(
        items=[_to_reading_read(item, container.code) for item in readings],
        total=total,
        limit=limit,
        offset=offset,
    )


def validate_fill_level(fill_level: float) -> None:
    """Garante o intervalo aceito de ocupação (0–100)."""
    if not 0.0 <= fill_level <= 100.0:
        raise UnprocessableError("O nível de ocupação deve estar entre 0 e 100.")
