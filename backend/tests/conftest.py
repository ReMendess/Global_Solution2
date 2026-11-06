"""Fixtures compartilhadas dos testes do backend.

O banco e o diretório de uploads são isolados em uma pasta temporária, definida
ANTES da importação da aplicação (a engine é criada no import de app.db.session).
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path

_TMP_ROOT = Path(tempfile.mkdtemp(prefix="cidade_limpa_tests_"))
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP_ROOT / 'test.db').as_posix()}"
os.environ["UPLOAD_DIR"] = str(_TMP_ROOT / "uploads")
os.environ["CONFIDENCE_THRESHOLD"] = "0.70"
# Isola os testes do modelo real publicado em ml/models/: por padrão não há pesos,
# para que os testes sejam determinísticos. Os testes de classificação publicam um
# modelo próprio via fixture (monkeypatch em settings).
os.environ["MODEL_PATH"] = str(_TMP_ROOT / "modelo_inexistente.keras")
os.environ["MODEL_METADATA_PATH"] = str(_TMP_ROOT / "modelo_inexistente.metadata.json")

import pytest  # noqa: E402
from app.core.enums import AlertLevel  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db.init_db import init_db  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.models.container import Container  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Cliente HTTP com o banco de teste criado e a aplicação completa."""
    init_db(engine)
    app = create_app()
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def _limpar_tabelas() -> Iterator[None]:
    """Mantém cada teste independente apagando os dados após a execução."""
    yield
    with engine.begin() as connection:
        for tabela in reversed(Base.metadata.sorted_tables):
            connection.execute(tabela.delete())


@pytest.fixture
def admin_headers() -> dict[str, str]:
    """Cabeçalho que identifica o perfil administrador."""
    return {"X-User-Role": "ADMIN"}


@pytest.fixture
def criar_container() -> Callable[..., str]:
    """Cria um contêiner de teste e devolve o código usado."""

    def _criar(
        code: str = "CONT-TESTE",
        neighborhood: str = "Pinheiros",
        fill_level: float = 0.0,
        alert_level: AlertLevel = AlertLevel.NORMAL,
    ) -> str:
        with SessionLocal() as db:
            db.add(
                Container(
                    code=code,
                    neighborhood=neighborhood,
                    address="Rua de Teste, 100",
                    capacity_liters=1000,
                    current_fill_level=fill_level,
                    alert_level=alert_level.value,
                    is_simulated=True,
                )
            )
            db.commit()
        return code

    return _criar
