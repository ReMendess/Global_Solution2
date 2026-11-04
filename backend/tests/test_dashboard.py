"""Testes dos indicadores do dashboard administrativo."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

SUMMARY = "/api/v1/dashboard/summary"
CONTAINERS = "/api/v1/dashboard/containers"
BAIRROS = "/api/v1/dashboard/neighborhoods"
OCORRENCIAS = "/api/v1/occurrences"

CriarContainer = Callable[..., str]


def _criar(client: TestClient, bairro: str, categoria: str, descricao: str) -> dict:
    """Cria uma ocorrência de apoio ao teste."""
    resposta = client.post(
        OCORRENCIAS,
        data={
            "neighborhood": bairro,
            "description": descricao,
            "reported_category": categoria,
        },
    )
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.mark.integration
def test_dashboard_exige_perfil_administrador(client: TestClient) -> None:
    """Todas as rotas de indicadores são restritas."""
    assert client.get(SUMMARY).status_code == 403
    assert client.get(CONTAINERS).status_code == 403
    assert client.get(BAIRROS).status_code == 403


@pytest.mark.integration
def test_resumo_reflete_dados_persistidos(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Os totais do resumo correspondem às ocorrências gravadas."""
    _criar(client, "Butantã", "OVERFLOW", "Contêiner cheio")
    _criar(client, "Tatuapé", "ILLEGAL_DUMPING", "Entulho na calçada")

    corpo = client.get(SUMMARY, headers=admin_headers).json()

    assert corpo["total_occurrences"] == 2
    assert corpo["by_category"]["OVERFLOW"] == 1
    assert corpo["by_category"]["ILLEGAL_DUMPING"] == 1
    assert sum(corpo["by_status"].values()) == 2
    assert corpo["needs_human_review"] == 2
    assert corpo["average_resolution_hours"] is None


@pytest.mark.integration
def test_tempo_medio_de_resolucao_considera_apenas_resolvidas(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """O tempo médio é calculado sobre ocorrências efetivamente resolvidas."""
    criada = _criar(client, "Butantã", "OVERFLOW", "Para resolver")
    for alvo in ("PENDING_DISPATCH", "DISPATCHED", "IN_PROGRESS"):
        client.patch(
            f"{OCORRENCIAS}/{criada['id']}/status",
            json={"status": alvo, "note": f"Transição para {alvo}."},
            headers=admin_headers,
        )
    client.patch(
        f"{OCORRENCIAS}/{criada['id']}/status",
        json={"status": "RESOLVED", "note": "Local limpo pela equipe."},
        headers=admin_headers,
    )

    corpo = client.get(SUMMARY, headers=admin_headers).json()

    assert corpo["by_status"]["RESOLVED"] == 1
    assert corpo["average_resolution_hours"] is not None
    assert corpo["average_resolution_hours"] >= 0


@pytest.mark.integration
def test_alertas_de_containers_agrupados(
    client: TestClient, criar_container: CriarContainer, admin_headers: dict[str, str]
) -> None:
    """O resumo de contêineres agrupa por nível e destaca os críticos."""
    criar_container(code="CONT-001", fill_level=10.0)
    criar_container(code="CONT-002", fill_level=95.0)
    client.post(
        "/api/v1/sensors/readings",
        json={"sensor_id": "SENSOR-002", "container_code": "CONT-002", "fill_level": 96.0},
    )

    corpo = client.get(CONTAINERS, headers=admin_headers).json()

    assert corpo["total_containers"] == 2
    assert corpo["by_alert_level"]["CRITICAL"] == 1
    assert corpo["critical_codes"] == ["CONT-002"]


@pytest.mark.integration
def test_ranking_de_bairros_ordenado_por_volume(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """O bairro com mais ocorrências aparece primeiro."""
    _criar(client, "Butantã", "OVERFLOW", "Ocorrência 1")
    _criar(client, "Butantã", "ILLEGAL_DUMPING", "Ocorrência 2")
    _criar(client, "Santana", "DAMAGED_CONTAINER", "Ocorrência 3")

    corpo = client.get(BAIRROS, headers=admin_headers).json()

    assert corpo["items"][0]["neighborhood"] == "Butantã"
    assert corpo["items"][0]["total"] == 2
    assert corpo["limit"] == 10
