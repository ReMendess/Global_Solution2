"""Testes das rotas de RPA (fila de demandas e execuções)."""

from __future__ import annotations

import pytest
from app.core.enums import OccurrenceCategory, OccurrenceStatus, Priority, RPAStatus
from app.db.session import SessionLocal
from app.models.occurrence import Occurrence
from fastapi.testclient import TestClient

QUEUE = "/api/v1/rpa/queue"
EXECUTIONS = "/api/v1/rpa/executions"


def _criar_ocorrencia(
    *,
    protocol: str,
    status: OccurrenceStatus = OccurrenceStatus.PENDING_DISPATCH,
    priority: Priority = Priority.MEDIUM,
) -> int:
    """Insere uma ocorrência diretamente no banco de teste."""
    with SessionLocal() as db:
        ocorrencia = Occurrence(
            protocol=protocol,
            category=OccurrenceCategory.OVERFLOW.value,
            neighborhood="Pinheiros",
            status=status.value,
            priority=priority.value,
            needs_human_review=False,
            is_simulated=True,
            description="Demanda de teste do RPA",
        )
        db.add(ocorrencia)
        db.commit()
        return ocorrencia.id


@pytest.mark.integration
def test_queue_lista_apenas_pending_em_ordem_de_prioridade(client: TestClient) -> None:
    """A fila retorna só PENDING_DISPATCH, ordenada por prioridade."""
    _criar_ocorrencia(protocol="CL-TEST-000001", priority=Priority.LOW)
    _criar_ocorrencia(protocol="CL-TEST-000002", priority=Priority.CRITICAL)
    _criar_ocorrencia(protocol="CL-TEST-000003", priority=Priority.HIGH)
    _criar_ocorrencia(protocol="CL-TEST-000004", status=OccurrenceStatus.DISPATCHED)

    resposta = client.get(QUEUE)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert [item["priority"] for item in corpo["items"]] == ["CRITICAL", "HIGH", "LOW"]
    assert all(item["category"] == "OVERFLOW" for item in corpo["items"])


@pytest.mark.integration
def test_execution_success_atualiza_ocorrencia(client: TestClient) -> None:
    """SUCCESS leva a ocorrência a DISPATCHED com o protocolo do portal."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000010")

    resposta = client.post(
        EXECUTIONS,
        json={
            "occurrence_id": ocorrencia_id,
            "status": "SUCCESS",
            "portal_protocol": "PORTAL-1234",
        },
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["status"] == "SUCCESS"
    assert corpo["portal_protocol"] == "PORTAL-1234"
    assert corpo["attempt"] == 1

    detalhe = client.get(
        f"/api/v1/occurrences/{ocorrencia_id}", headers={"X-User-Role": "ADMIN"}
    ).json()
    assert detalhe["status"] == "DISPATCHED"
    assert detalhe["dispatch_protocol"] == "PORTAL-1234"
    ultimo = detalhe["status_history"][-1]
    assert ultimo["to_status"] == "DISPATCHED"
    assert ultimo["changed_by"] == "RPA"


@pytest.mark.integration
def test_execution_success_duplicada_retorna_409(client: TestClient) -> None:
    """A segunda execução SUCCESS para a mesma ocorrência é bloqueada."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000011")

    primeira = client.post(
        EXECUTIONS,
        json={"occurrence_id": ocorrencia_id, "status": "SUCCESS", "portal_protocol": "PORTAL-1"},
    )
    assert primeira.status_code == 201

    segunda = client.post(
        EXECUTIONS,
        json={"occurrence_id": ocorrencia_id, "status": "SUCCESS", "portal_protocol": "PORTAL-2"},
    )

    assert segunda.status_code == 409
    assert "já foi despachada" in segunda.json()["detail"]


@pytest.mark.integration
def test_execution_success_sem_protocolo_retorna_409(client: TestClient) -> None:
    """SUCCESS exige o protocolo do portal capturado."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000012")

    resposta = client.post(EXECUTIONS, json={"occurrence_id": ocorrencia_id, "status": "SUCCESS"})

    assert resposta.status_code == 409
    assert "portal_protocol" in resposta.json()["detail"]


@pytest.mark.integration
def test_execution_failed_mantem_pending_e_incrementa_tentativa(
    client: TestClient,
) -> None:
    """FAILED não altera o status e a tentativa é incrementada na repetição."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000013")

    primeira = client.post(
        EXECUTIONS,
        json={
            "occurrence_id": ocorrencia_id,
            "status": "FAILED",
            "error_message": "portal fora do ar",
        },
    )
    segunda = client.post(
        EXECUTIONS,
        json={"occurrence_id": ocorrencia_id, "status": "FAILED", "error_message": "timeout"},
    )

    assert primeira.status_code == 201
    assert segunda.status_code == 201
    assert primeira.json()["attempt"] == 1
    assert segunda.json()["attempt"] == 2

    detalhe = client.get(
        f"/api/v1/occurrences/{ocorrencia_id}", headers={"X-User-Role": "ADMIN"}
    ).json()
    assert detalhe["status"] == "PENDING_DISPATCH"


@pytest.mark.integration
def test_execution_para_ocorrencia_fora_da_fila_retorna_409(client: TestClient) -> None:
    """Só ocorrências em PENDING_DISPATCH podem ser despachadas."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000014", status=OccurrenceStatus.RESOLVED)

    resposta = client.post(
        EXECUTIONS,
        json={"occurrence_id": ocorrencia_id, "status": "SUCCESS", "portal_protocol": "PORTAL-9"},
    )

    assert resposta.status_code == 409
    assert "PENDING_DISPATCH" in resposta.json()["detail"]


@pytest.mark.integration
def test_execution_para_ocorrencia_inexistente_retorna_404(client: TestClient) -> None:
    """Ocorrência desconhecida é rejeitada com 404."""
    resposta = client.post(EXECUTIONS, json={"occurrence_id": 999999, "status": "FAILED"})

    assert resposta.status_code == 404


@pytest.mark.integration
def test_historico_de_execucoes_exige_admin(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Sem o perfil ADMIN, o histórico responde 403."""
    ocorrencia_id = _criar_ocorrencia(protocol="CL-TEST-000015")
    client.post(
        EXECUTIONS,
        json={"occurrence_id": ocorrencia_id, "status": "SUCCESS", "portal_protocol": "PORTAL-7"},
    )

    assert client.get(EXECUTIONS).status_code == 403

    resposta = client.get(EXECUTIONS, headers=admin_headers)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 1
    assert corpo["items"][0]["status"] == RPAStatus.SUCCESS.value
