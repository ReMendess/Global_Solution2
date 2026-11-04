"""Testes da rota de saúde."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_health_retorna_ok(client: TestClient) -> None:
    """A API deve responder 200 com banco acessível."""
    resposta = client.get("/health")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "ok"
    assert corpo["database"] == "ok"
    assert corpo["environment"] == "test"
    assert corpo["version"]


@pytest.mark.integration
def test_health_indica_modelo_indisponivel_na_fase_1(client: TestClient) -> None:
    """Sem pesos treinados, o campo model_loaded deve ser falso."""
    corpo = client.get("/health").json()

    assert corpo["model_loaded"] is False
