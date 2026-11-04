"""Engine e sessões do SQLAlchemy apontando para o SQLite do projeto."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _engine_kwargs(url: str) -> dict[str, Any]:
    """Argumentos específicos do SQLite (threads do Uvicorn e timeout de escrita)."""
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False, "timeout": 15}}
    return {}


def _ensure_sqlite_directory(url: str) -> None:
    """Garante que a pasta do arquivo .db exista antes de abrir a conexão."""
    prefixo = "sqlite:///"
    if not url.startswith(prefixo):
        return
    caminho = Path(url[len(prefixo) :])
    if caminho.parent and str(caminho) != ":memory:":
        caminho.parent.mkdir(parents=True, exist_ok=True)


def get_engine() -> Engine:
    """Cria o engine a partir das configurações atuais (usado também nos testes)."""
    url = get_settings().resolved_database_url
    _ensure_sqlite_directory(url)
    return create_engine(url, future=True, **_engine_kwargs(url))


engine: Engine = get_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dependência FastAPI que entrega uma sessão por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
