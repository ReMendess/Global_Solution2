"""Testes da rota de metadados (enums canônicos)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_enums_refletem_o_project_context(client: TestClient) -> None:
    """Os valores retornados devem ser exatamente os definidos no desafio."""
    corpo = client.get("/api/v1/meta/enums").json()

    assert set(corpo["categories"]) == {
        "ILLEGAL_DUMPING",
        "OVERFLOW",
        "DAMAGED_CONTAINER",
        "OTHER",
    }
    assert set(corpo["model_labels"]) == {"REGULAR", "IRREGULAR"}
    assert set(corpo["statuses"]) == {
        "OPEN",
        "CLASSIFIED",
        "PENDING_DISPATCH",
        "DISPATCHED",
        "IN_PROGRESS",
        "RESOLVED",
        "REJECTED",
    }
    assert set(corpo["priorities"]) == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
    assert set(corpo["alert_levels"]) == {"NORMAL", "HIGH", "CRITICAL"}
    assert set(corpo["user_roles"]) == {"CITIZEN", "ADMIN"}
    assert set(corpo["rpa_statuses"]) == {"SUCCESS", "FAILED", "SKIPPED"}


@pytest.mark.integration
def test_estados_terminais_nao_tem_transicoes(client: TestClient) -> None:
    """RESOLVED e REJECTED não podem voltar para a fila do RPA."""
    transicoes = client.get("/api/v1/meta/enums").json()["allowed_transitions"]

    assert transicoes["RESOLVED"] == []
    assert transicoes["REJECTED"] == []
    assert "DISPATCHED" in transicoes["PENDING_DISPATCH"]
