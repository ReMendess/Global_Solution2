"""Testes de integração de contêineres e telemetria dos sensores."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

SENSORES = "/api/v1/sensors/readings"
CONTAINERS = "/api/v1/containers"

CriarContainer = Callable[..., str]


def _enviar(client: TestClient, container_code: str, fill_level: float) -> dict:
    """Envia uma leitura de sensor e devolve o corpo da resposta."""
    return client.post(
        SENSORES,
        json={
            "sensor_id": "SENSOR-001",
            "container_code": container_code,
            "fill_level": fill_level,
            "distance_cm": 12.5,
        },
    ).json()


@pytest.mark.integration
def test_leitura_critica_atualiza_container(
    client: TestClient, criar_container: CriarContainer
) -> None:
    """Ocupação de 95% deriva alerta CRITICAL e atualiza o contêiner."""
    codigo = criar_container()

    resposta = client.post(
        SENSORES,
        json={"sensor_id": "SENSOR-001", "container_code": codigo, "fill_level": 95.0},
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert corpo["alert_level"] == "CRITICAL"
    assert corpo["is_simulated"] is True
    assert corpo["container_code"] == codigo

    container = client.get(f"{CONTAINERS}/{codigo}").json()
    assert container["current_fill_level"] == 95.0
    assert container["alert_level"] == "CRITICAL"
    assert container["last_reading_at"] is not None


@pytest.mark.integration
@pytest.mark.parametrize(
    ("nivel", "esperado"),
    [(45.0, "NORMAL"), (80.0, "HIGH"), (89.9, "HIGH"), (90.0, "CRITICAL")],
)
def test_limiares_aplicados_na_ingestao(
    client: TestClient, criar_container: CriarContainer, nivel: float, esperado: str
) -> None:
    """Os limiares do desafio são aplicados no momento da ingestão."""
    codigo = criar_container()

    assert _enviar(client, codigo, nivel)["alert_level"] == esperado


@pytest.mark.integration
def test_container_desconhecido_retorna_404(client: TestClient) -> None:
    """Leitura para contêiner inexistente é rejeitada."""
    resposta = client.post(
        SENSORES,
        json={"sensor_id": "SENSOR-999", "container_code": "CONT-NAO-EXISTE", "fill_level": 50.0},
    )

    assert resposta.status_code == 404
    assert "não encontrado" in resposta.json()["detail"]


@pytest.mark.integration
def test_nivel_fora_do_intervalo_retorna_422(
    client: TestClient, criar_container: CriarContainer
) -> None:
    """Ocupação precisa estar entre 0 e 100."""
    codigo = criar_container()

    resposta = client.post(
        SENSORES,
        json={"sensor_id": "SENSOR-001", "container_code": codigo, "fill_level": 130.0},
    )

    assert resposta.status_code == 422


@pytest.mark.integration
def test_historico_de_leituras_ordenado_do_mais_recente(
    client: TestClient, criar_container: CriarContainer, admin_headers: dict[str, str]
) -> None:
    """O histórico é paginado e traz as leituras mais recentes primeiro."""
    codigo = criar_container()
    _enviar(client, codigo, 20.0)
    _enviar(client, codigo, 65.0)
    _enviar(client, codigo, 93.0)

    resposta = client.get(
        f"{CONTAINERS}/{codigo}/readings", params={"limit": 2}, headers=admin_headers
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 3
    assert len(corpo["items"]) == 2
    assert corpo["items"][0]["fill_level"] == 93.0
    assert corpo["items"][0]["alert_level"] == "CRITICAL"


@pytest.mark.integration
def test_listagem_de_containers_exige_admin(
    client: TestClient, criar_container: CriarContainer, admin_headers: dict[str, str]
) -> None:
    """A lista completa é restrita ao perfil administrativo."""
    criar_container(code="CONT-001", neighborhood="Pinheiros")

    assert client.get(CONTAINERS).status_code == 403

    resposta = client.get(CONTAINERS, headers=admin_headers)
    assert resposta.status_code == 200
    assert resposta.json()["total"] == 1
