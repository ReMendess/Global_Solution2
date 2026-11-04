"""Rota de ingestão de telemetria dos sensores virtuais (ESP32 simulado)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.container import SensorReadingCreate, SensorReadingRead
from app.services import container_service

router = APIRouter(prefix="/api/v1/sensors", tags=["sensores"])


@router.post(
    "/readings",
    response_model=SensorReadingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Recebe a telemetria de um sensor virtual",
)
def register_reading(
    payload: SensorReadingCreate,
    db: Session = Depends(get_db),
) -> SensorReadingRead:
    """Persiste a leitura, deriva o alerta pelos limiares e atualiza o contêiner.

    Rota de uso interno do simulador (FASE 4); não expõe dados pessoais.
    """
    return container_service.register_reading(db, payload)
