"""Criação do schema e preparação de diretórios de runtime."""

from __future__ import annotations

import logging

from sqlalchemy.engine import Engine

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_engine

logger = logging.getLogger(__name__)


def init_db(engine: Engine | None = None) -> None:
    """Cria as tabelas do projeto (ADR-003: sem migrações, SQLite local)."""
    # Importa os módulos de modelo para registrar as tabelas no metadata.
    from app import models  # noqa: F401  (efeito colateral: registro das tabelas)

    target = engine or get_engine()
    Base.metadata.create_all(bind=target)
    logger.info("Schema criado/verificado em %s", target.url)


def ensure_runtime_directories() -> None:
    """Cria o diretório de uploads usado pelo registro de ocorrências."""
    upload_dir = get_settings().resolved_upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
