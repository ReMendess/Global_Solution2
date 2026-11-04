"""Rota de verificação de saúde da aplicação."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.schemas.health import HealthRead
from app.services import classification_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["saúde"])


@router.get("/health", response_model=HealthRead, summary="Status da API")
def health_check(db: Session = Depends(get_db)) -> HealthRead:
    """Informa se a API está no ar, se o banco responde e se há modelo carregado."""
    settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:  # noqa: BLE001 - qualquer falha de conexão marca o banco como indisponível
        logger.exception("Falha ao consultar o banco de dados no health check")
        database = "error"

    return HealthRead(
        status="ok" if database == "ok" else "degraded",
        version=settings.app_version,
        environment=settings.app_env,
        database=database,
        model_loaded=classification_service.is_model_available(),
    )
