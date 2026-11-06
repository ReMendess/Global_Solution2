"""Testes de integração do agente conversacional (via HTTP, sobre dados reais)."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from app.core.enums import AlertLevel
from app.services.agent.session import session_store
from fastapi.testclient import TestClient

MESSAGES = "/api/v1/agent/messages"
SESSIONS = "/api/v1/agent/sessions"


@pytest.fixture(autouse=True)
def _limpar_contexto_sessao():
    """Isola o contexto em memória entre testes."""
    session_store.clear()
    yield
    session_store.clear()


def _enviar(client: TestClient, session_id: str, mensagem: str) -> dict:
    resposta = client.post(MESSAGES, json={"session_id": session_id, "message": mensagem})
    assert resposta.status_code == 200, resposta.text
    return resposta.json()


@pytest.mark.integration
def test_mensagem_desconhecida_recebe_orientacao(client: TestClient) -> None:
    """Pergunta fora do domínio recebe resposta de orientação, sem inventar dados."""
    corpo = _enviar(client, "sess-orientacao", "qual a previsão do tempo?")

    assert corpo["intent"] == "desconhecida"
    assert corpo["tool_used"] is None
    assert corpo["data"] is None
    assert "Não entendi" in corpo["response"]


@pytest.mark.integration
def test_consulta_ocorrencia_por_protocolo_real(client: TestClient) -> None:
    """O agente devolve o status real de uma ocorrência persistida."""
    criada = _enviar(client, "sess-1", "registrar ocorrência de transbordamento em Pinheiros")
    protocolo = criada["data"]["protocol"]

    resposta = _enviar(client, "sess-1", f"status da ocorrência {protocolo}")

    assert resposta["intent"] == "consultar_ocorrencia"
    assert resposta["tool_used"] == "consultar_ocorrencia"
    assert resposta["data"]["protocol"] == protocolo
    assert resposta["data"]["status"] in {"OPEN", "CLASSIFIED", "PENDING_DISPATCH"}


@pytest.mark.integration
def test_continuidade_sem_protocolo_usa_contexto(client: TestClient) -> None:
    """Depois de consultar por protocolo, o agente lembra a ocorrência."""
    criada = _enviar(client, "sess-2", "registrar ocorrência em Vila Madalena")
    protocolo = criada["data"]["protocol"]
    _enviar(client, "sess-2", f"status da ocorrência {protocolo}")

    # Segunda pergunta não repete o protocolo.
    resposta = _enviar(client, "sess-2", "e o status?")

    assert resposta["intent"] == "consultar_ocorrencia"
    assert resposta["data"]["protocol"] == protocolo


@pytest.mark.integration
def test_consulta_container_real(client: TestClient, criar_container: Callable[..., str]) -> None:
    """O agente devolve a ocupação real de um contêiner."""
    criar_container(
        code="CONT-AGENTE", neighborhood="Pinheiros", fill_level=85.0, alert_level=AlertLevel.HIGH
    )

    resposta = _enviar(client, "sess-3", "nível do contêiner CONT-AGENTE")

    assert resposta["tool_used"] == "consultar_container"
    assert resposta["data"]["code"] == "CONT-AGENTE"
    assert "85" in resposta["response"]
    assert resposta["data"]["alert_level"] == "HIGH"


@pytest.mark.integration
def test_listar_pontos_de_coleta(client: TestClient, criar_container: Callable[..., str]) -> None:
    """A ferramenta lista os contêineres cadastrados (pontos de coleta)."""
    criar_container(code="CONT-P1", neighborhood="Pinheiros")
    criar_container(code="CONT-P2", neighborhood="Butantã", fill_level=95.0)

    resposta = _enviar(client, "sess-4", "quais são os pontos de coleta?")

    assert resposta["tool_used"] == "listar_pontos_coleta"
    assert resposta["data"]["total"] == 2
    codigos = {item["code"] for item in resposta["data"]["containers"]}
    assert codigos == {"CONT-P1", "CONT-P2"}


@pytest.mark.integration
def test_criar_ocorrencia_exige_bairro(client: TestClient) -> None:
    """Sem bairro informado, o agente pede o dado que falta (não inventa)."""
    resposta = _enviar(client, "sess-5", "registrar ocorrência de transbordamento")

    assert resposta["tool_used"] is None
    assert "bairro" in resposta["response"].lower()


@pytest.mark.integration
def test_consultar_indicadores(client: TestClient) -> None:
    """A ferramenta devolve os indicadores reais do dashboard."""
    _enviar(client, "sess-6", "registrar ocorrência em Santana")

    resposta = _enviar(client, "sess-6", "quantas ocorrências existem?")

    assert resposta["tool_used"] == "consultar_indicadores"
    assert resposta["data"]["total_occurrences"] >= 1


@pytest.mark.integration
def test_historico_da_sessao_persistido(client: TestClient) -> None:
    """As interações são persistidas e recuperadas pelo histórico."""
    _enviar(client, "sess-7", "registrar ocorrência em Tatuapé")
    _enviar(client, "sess-7", "indicadores")

    resposta = client.get(f"{SESSIONS}/sess-7")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 2
    assert [item["intent"] for item in corpo["interactions"]] == [
        "criar_ocorrencia",
        "consultar_indicadores",
    ]
