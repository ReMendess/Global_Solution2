"""Testes de integração da visão administrativa de ocorrências."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

ENDPOINT = "/api/v1/occurrences"


def _criar(client: TestClient, **campos: str) -> dict:
    """Cria uma ocorrência de apoio ao teste."""
    dados = {"neighborhood": "Pinheiros", "description": "Apoio"}
    dados.update(campos)
    resposta = client.post(ENDPOINT, data=dados)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.mark.integration
def test_listagem_exige_perfil_administrador(client: TestClient) -> None:
    """Sem o cabeçalho de perfil, a listagem é negada."""
    resposta = client.get(ENDPOINT)

    assert resposta.status_code == 403
    assert "ADMIN" in resposta.json()["detail"]


@pytest.mark.integration
def test_listagem_retorna_total_e_itens(client: TestClient, admin_headers: dict[str, str]) -> None:
    """A listagem paginada reflete os registros persistidos."""
    _criar(client, neighborhood="Butantã")
    _criar(client, neighborhood="Tatuapé")

    resposta = client.get(ENDPOINT, headers=admin_headers)

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 2
    assert len(corpo["items"]) == 2
    assert corpo["limit"] == 20
    assert corpo["offset"] == 0


@pytest.mark.integration
def test_listagem_filtra_por_categoria_e_revisao(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Filtros por categoria e por necessidade de revisão funcionam juntos."""
    _criar(client, neighborhood="Butantã", reported_category="OVERFLOW")
    _criar(client, neighborhood="Tatuapé", reported_category="OTHER")

    por_categoria = client.get(
        ENDPOINT, params={"category": "OVERFLOW"}, headers=admin_headers
    ).json()
    por_revisao = client.get(
        ENDPOINT, params={"needs_human_review": "true"}, headers=admin_headers
    ).json()

    assert por_categoria["total"] == 1
    assert por_categoria["items"][0]["neighborhood"] == "Butantã"
    assert por_revisao["total"] == 2


@pytest.mark.integration
def test_listagem_paginada_com_offset(client: TestClient, admin_headers: dict[str, str]) -> None:
    """limit e offset controlam a página devolvida."""
    for indice, bairro in enumerate(["Butantã", "Tatuapé", "Santana"], start=1):
        _criar(client, neighborhood=bairro, description=f"Ocorrência {indice}")

    primeira = client.get(ENDPOINT, params={"limit": 2, "offset": 0}, headers=admin_headers).json()
    segunda = client.get(ENDPOINT, params={"limit": 2, "offset": 2}, headers=admin_headers).json()

    assert primeira["total"] == 3
    assert len(primeira["items"]) == 2
    assert len(segunda["items"]) == 1


@pytest.mark.integration
def test_detalhe_exige_admin_e_retorna_404_quando_ausente(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Detalhe por id valida perfil e existência do registro."""
    criada = _criar(client, neighborhood="Pinheiros")

    assert client.get(f"{ENDPOINT}/{criada['id']}").status_code == 403

    ok = client.get(f"{ENDPOINT}/{criada['id']}", headers=admin_headers)
    assert ok.status_code == 200
    assert ok.json()["protocol"] == criada["protocol"]

    ausente = client.get(f"{ENDPOINT}/999999", headers=admin_headers)
    assert ausente.status_code == 404


@pytest.mark.integration
def test_transicao_valida_de_status_registra_auditoria(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """OPEN -> PENDING_DISPATCH é permitida e fica registrada no histórico."""
    criada = _criar(client, neighborhood="Butantã")

    resposta = client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "PENDING_DISPATCH", "note": "Revisão humana aprovou o envio."},
        headers=admin_headers,
    )

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "PENDING_DISPATCH"
    ultimo = corpo["status_history"][-1]
    assert ultimo["from_status"] == "OPEN"
    assert ultimo["to_status"] == "PENDING_DISPATCH"
    assert ultimo["changed_by"] == "ADMIN"


@pytest.mark.integration
def test_transicao_invalida_retorna_409(client: TestClient, admin_headers: dict[str, str]) -> None:
    """Pular etapas da máquina de estados é bloqueado."""
    criada = _criar(client, neighborhood="Butantã")
    client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "PENDING_DISPATCH"},
        headers=admin_headers,
    )

    resposta = client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "CLASSIFIED"},
        headers=admin_headers,
    )

    assert resposta.status_code == 409
    assert "não é permitida" in resposta.json()["detail"]


@pytest.mark.integration
def test_transicao_terminal_exige_observacao(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Transições terminais exigem justificativa."""
    criada = _criar(client, neighborhood="Butantã")

    sem_nota = client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "REJECTED"},
        headers=admin_headers,
    )
    com_nota = client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "REJECTED", "note": "Registro duplicado de outro protocolo."},
        headers=admin_headers,
    )

    assert sem_nota.status_code == 422
    assert com_nota.status_code == 200
    assert com_nota.json()["status"] == "REJECTED"


@pytest.mark.integration
def test_estado_terminal_nao_aceita_nova_transicao(
    client: TestClient, admin_headers: dict[str, str]
) -> None:
    """Depois de REJECTED a ocorrência não retorna ao fluxo."""
    criada = _criar(client, neighborhood="Butantã")
    client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "REJECTED", "note": "Fora do escopo atendido."},
        headers=admin_headers,
    )

    resposta = client.patch(
        f"{ENDPOINT}/{criada['id']}/status",
        json={"status": "PENDING_DISPATCH"},
        headers=admin_headers,
    )

    assert resposta.status_code == 409
