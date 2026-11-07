"""Aplicação FastAPI do Smart Clean City."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import (
    agent,
    classification,
    containers,
    dashboard,
    health,
    meta,
    occurrences,
    rpa,
    sensors,
)
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.init_db import ensure_runtime_directories, init_db

logger = logging.getLogger(__name__)

DESCRIPTION = """
Plataforma Inteligente de Monitoramento e Gestão de Resíduos Urbanos.

O FastAPI é o núcleo da solução: recebe ocorrências com foto, coordena a
classificação por visão computacional, ingere telemetria de contêineres
simulados e serve os indicadores do dashboard administrativo.
"""


def configure_logging() -> None:
    """Configura o log da aplicação (uma única vez por processo)."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Prepara banco e diretórios de runtime no startup da aplicação."""
    configure_logging()
    init_db()
    ensure_runtime_directories()
    logger.info("Smart Clean City API iniciada")
    yield
    logger.info("Smart Clean City API encerrada")


def create_app() -> FastAPI:
    """Cria e configura a instância da aplicação."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=DESCRIPTION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def handle_app_error(_: Request, exc: AppError) -> JSONResponse:
        """Traduz erros de regra de negócio para o status HTTP correspondente."""
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        """Evita vazar detalhes internos ao cliente e mantém o rastro no log."""
        logger.exception("Erro não tratado na API", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Erro interno ao processar a solicitação."},
        )

    app.include_router(health.router)
    app.include_router(meta.router)
    app.include_router(occurrences.router)
    app.include_router(containers.router)
    app.include_router(sensors.router)
    app.include_router(dashboard.router)
    app.include_router(classification.router)
    app.include_router(rpa.router)
    app.include_router(agent.router)

    # Imagens enviadas ficam em data/uploads (ADR-005); o frontend as carrega por URL.
    upload_dir = settings.resolved_upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    return app


app = create_app()
