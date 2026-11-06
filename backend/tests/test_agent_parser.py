"""Testes do interpretador de intenções (regras e palavras-chave)."""

from __future__ import annotations

import pytest
from app.core.enums import OccurrenceCategory
from app.services.agent.intent_parser import (
    INTENT_CONSULTAR_CONTAINER,
    INTENT_CONSULTAR_INDICADORES,
    INTENT_CONSULTAR_OCORRENCIA,
    INTENT_CRIAR_OCORRENCIA,
    INTENT_DESCONHECIDA,
    INTENT_LISTAR_PONTOS,
    parse,
)


@pytest.mark.unit
def test_consulta_ocorrencia_por_protocolo() -> None:
    """Protocolo explícito é reconhecido como consulta de ocorrência."""
    resultado = parse("Qual o status da ocorrência CL-2026-000012?")

    assert resultado.intent == INTENT_CONSULTAR_OCORRENCIA
    assert resultado.args["protocol"] == "CL-2026-000012"


@pytest.mark.unit
def test_consulta_ocorrencia_sem_protocolo() -> None:
    """Ocorrência sem protocolo continua sendo consulta de ocorrência."""
    resultado = parse("qual o andamento da minha ocorrência")

    assert resultado.intent == INTENT_CONSULTAR_OCORRENCIA
    assert "protocol" not in resultado.args


@pytest.mark.unit
def test_consulta_container_por_codigo() -> None:
    """Código de contêiner é reconhecido."""
    resultado = parse("nível do contêiner CONT-003")

    assert resultado.intent == INTENT_CONSULTAR_CONTAINER
    assert resultado.args["code"] == "CONT-003"


@pytest.mark.unit
def test_consulta_container_por_palavra() -> None:
    """'Contêiner' sem código também vira consulta de contêiner."""
    assert parse("qual o nível da lixeira?").intent == INTENT_CONSULTAR_CONTAINER


@pytest.mark.unit
def test_listar_pontos_de_coleta() -> None:
    assert parse("quais são os pontos de coleta?").intent == INTENT_LISTAR_PONTOS
    assert parse("onde posso descartar?").intent == INTENT_LISTAR_PONTOS


@pytest.mark.unit
def test_consultar_indicadores() -> None:
    assert parse("quantas ocorrências?").intent == INTENT_CONSULTAR_INDICADORES
    assert parse("mostre os indicadores").intent == INTENT_CONSULTAR_INDICADORES


@pytest.mark.unit
def test_criar_ocorrencia_com_bairro_e_categoria() -> None:
    resultado = parse("registrar ocorrência de transbordamento em Pinheiros")

    assert resultado.intent == INTENT_CRIAR_OCORRENCIA
    assert resultado.args["neighborhood"] == "Pinheiros"
    assert resultado.args["category"] == OccurrenceCategory.OVERFLOW


@pytest.mark.unit
def test_criar_ocorrencia_com_entulho() -> None:
    resultado = parse("denunciar descarte irregular de entulho no Butantã")

    assert resultado.intent == INTENT_CRIAR_OCORRENCIA
    assert resultado.args["neighborhood"] == "Butantã"
    assert resultado.args["category"] == OccurrenceCategory.ILLEGAL_DUMPING


@pytest.mark.unit
def test_criar_ocorrencia_sem_bairro() -> None:
    resultado = parse("registrar uma ocorrência de transbordamento")

    assert resultado.intent == INTENT_CRIAR_OCORRENCIA
    assert resultado.args["neighborhood"] is None


@pytest.mark.unit
def test_mensagem_desconhecida() -> None:
    assert parse("qual a previsão do tempo?").intent == INTENT_DESCONHECIDA
