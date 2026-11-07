"""Teste de integração ponta a ponta do fluxo de uma ocorrência.

Cobre o ciclo completo da ocorrência, usando o banco de testes (temporário):

1. registro (OPEN);
2. envio para a fila do RPA (PENDING_DISPATCH);
3. despacho via RPA (DISPATCHED + protocolo do portal);
4. resolução (IN_PROGRESS → RESOLVED);

com a trilha de auditoria (`status_history`) verificada em cada passo.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from app.core.config import get_settings
from app.services import classification_service
from fastapi.testclient import TestClient
from PIL import Image

OCORRENCIAS = "/api/v1/occurrences"
RPA_QUEUE = "/api/v1/rpa/queue"
RPA_EXECUTIONS = "/api/v1/rpa/executions"


def _criar_ocorrencia(client: TestClient, **campos: str) -> dict:
    """Cria uma ocorrência sem foto e devolve o corpo."""
    dados = {"neighborhood": "Barra Funda", "description": "e2e", "reported_category": "OVERFLOW"}
    dados.update(campos)
    resposta = client.post(OCORRENCIAS, data=dados)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.mark.integration
def test_fluxo_completo_de_ocorrencia(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Registro → fila → despacho RPA → resolução, com trilha de auditoria."""
    # 1. registro
    ocorrencia = _criar_ocorrencia(client)
    assert ocorrencia["status"] == "OPEN"

    # 2. admin envia para a fila
    resposta = client.patch(
        f"{OCORRENCIAS}/{ocorrencia['id']}/status",
        json={"status": "PENDING_DISPATCH"},
        headers=admin_headers,
    )
    assert resposta.status_code == 200

    # 3. a ocorrência aparece na fila do RPA
    fila = client.get(RPA_QUEUE).json()
    assert any(item["occurrence_id"] == ocorrencia["id"] for item in fila["items"])

    # 4. RPA despacha
    resposta = client.post(
        RPA_EXECUTIONS,
        json={
            "occurrence_id": ocorrencia["id"],
            "status": "SUCCESS",
            "portal_protocol": "PORTAL-E2E-1",
            "duration_ms": 1200,
        },
    )
    assert resposta.status_code == 201, resposta.text
    detalhe = client.get(f"{OCORRENCIAS}/{ocorrencia['id']}", headers=admin_headers).json()
    assert detalhe["status"] == "DISPATCHED"
    assert detalhe["dispatch_protocol"] == "PORTAL-E2E-1"

    # 5. resolução
    assert (
        client.patch(
            f"{OCORRENCIAS}/{ocorrencia['id']}/status",
            json={"status": "IN_PROGRESS"},
            headers=admin_headers,
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"{OCORRENCIAS}/{ocorrencia['id']}/status",
            json={"status": "RESOLVED", "note": "Local limpo pela equipe."},
            headers=admin_headers,
        ).status_code
        == 200
    )

    # 6. estado final e trilha completa
    final = client.get(f"{OCORRENCIAS}/{ocorrencia['id']}", headers=admin_headers).json()
    assert final["status"] == "RESOLVED"
    assert [item["to_status"] for item in final["status_history"]] == [
        "OPEN",
        "PENDING_DISPATCH",
        "DISPATCHED",
        "IN_PROGRESS",
        "RESOLVED",
    ]

    # 7. a execução do RPA ficou registrada
    execucoes = client.get(RPA_EXECUTIONS, headers=admin_headers).json()
    assert execucoes["total"] == 1
    assert execucoes["items"][0]["status"] == "SUCCESS"
    assert execucoes["items"][0]["portal_protocol"] == "PORTAL-E2E-1"


# ---------------------------------------------------------------------------
# Fluxo completo com visão computacional (modelo de fixture)
# ---------------------------------------------------------------------------
def _png() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (64, 64), (110, 150, 90)).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.fixture
def modelo_publicado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Publica um modelo Keras mínimo para exercitar a classificação no fluxo."""
    import keras

    pesos = tmp_path / "e2e.keras"
    metadados = tmp_path / "e2e.metadata.json"

    entradas = keras.Input(shape=(224, 224, 3), name="imagem")
    x = keras.layers.Rescaling(1.0 / 127.5, offset=-1.0, name="normalizacao")(entradas)
    x = keras.layers.Conv2D(8, 3, strides=16, activation="relu", name="reducao")(x)
    x = keras.layers.GlobalAveragePooling2D(name="pooling_global")(x)
    saidas = keras.layers.Dense(2, activation="softmax", name="classes")(x)
    modelo = keras.Model(entradas, saidas, name="modelo_e2e")
    modelo.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    modelo.save(pesos)

    metadados.write_text(
        json.dumps(
            {"model_version": "e2e-v0", "classes": ["REGULAR", "IRREGULAR"], "image_size": 224}
        ),
        encoding="utf-8",
    )

    settings = get_settings()
    monkeypatch.setattr(settings, "model_path", pesos)
    monkeypatch.setattr(settings, "model_metadata_path", metadados)
    monkeypatch.setattr(settings, "confidence_threshold", 0.0)
    classification_service.reset_cache()

    yield

    classification_service.reset_cache()


@pytest.mark.integration
def test_fluxo_com_ml_de_ponta_a_ponta(
    client: TestClient, admin_headers: dict[str, str], modelo_publicado
) -> None:
    """Registra com foto (classifica) → despacha → resolve."""
    resposta = client.post(
        OCORRENCIAS,
        data={"neighborhood": "Vila Mariana", "reported_category": "OVERFLOW"},
        files={"image": ("foto.png", _png(), "image/png")},
    )
    assert resposta.status_code == 201, resposta.text
    ocorrencia = resposta.json()

    assert ocorrencia["model_label"] in {"REGULAR", "IRREGULAR"}
    assert ocorrencia["confidence"] is not None
    assert ocorrencia["model_version"] == "e2e-v0"
    assert ocorrencia["status"] == "PENDING_DISPATCH"

    resposta = client.post(
        RPA_EXECUTIONS,
        json={
            "occurrence_id": ocorrencia["id"],
            "status": "SUCCESS",
            "portal_protocol": "PORTAL-E2E-2",
        },
    )
    assert resposta.status_code == 201

    client.patch(
        f"{OCORRENCIAS}/{ocorrencia['id']}/status",
        json={"status": "IN_PROGRESS"},
        headers=admin_headers,
    )
    client.patch(
        f"{OCORRENCIAS}/{ocorrencia['id']}/status",
        json={"status": "RESOLVED", "note": "Resolvido no fluxo com ML."},
        headers=admin_headers,
    )

    final = client.get(f"{OCORRENCIAS}/{ocorrencia['id']}", headers=admin_headers).json()
    assert final["status"] == "RESOLVED"
    assert [item["to_status"] for item in final["status_history"]] == [
        "OPEN",
        "CLASSIFIED",
        "PENDING_DISPATCH",
        "DISPATCHED",
        "IN_PROGRESS",
        "RESOLVED",
    ]
