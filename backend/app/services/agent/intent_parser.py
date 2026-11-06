"""Interpretador de intenções do agente (por regras e palavras-chave, sem LLM)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from app.core.enums import OccurrenceCategory

# --- intenções reconhecidas ---
INTENT_CONSULTAR_OCORRENCIA = "consultar_ocorrencia"
INTENT_CONSULTAR_CONTAINER = "consultar_container"
INTENT_LISTAR_PONTOS = "listar_pontos_coleta"
INTENT_CRIAR_OCORRENCIA = "criar_ocorrencia"
INTENT_CONSULTAR_INDICADORES = "consultar_indicadores"
INTENT_DESCONHECIDA = "desconhecida"

ALL_INTENTS = (
    INTENT_CONSULTAR_OCORRENCIA,
    INTENT_CONSULTAR_CONTAINER,
    INTENT_LISTAR_PONTOS,
    INTENT_CRIAR_OCORRENCIA,
    INTENT_CONSULTAR_INDICADORES,
    INTENT_DESCONHECIDA,
)

_PROTOCOL_RE = re.compile(r"(CL-\d{4}-\d{1,7})", re.IGNORECASE)
_CONTAINER_RE = re.compile(r"(CONT-[A-Za-z0-9-]+)", re.IGNORECASE)
_NEIGHBORHOOD_RE = re.compile(r"(?:em|no|na)\s+([A-ZÀ-Ü][A-Za-zÀ-ü]+(?:\s+[A-ZÀ-Ü][A-Za-zÀ-ü]+)*)")

_CRIAR_KEYWORDS = (
    "registrar",
    "denunciar",
    "reportar",
    "nova ocorrência",
    "nova ocorrencia",
    "abrir ocorrência",
    "criar ocorrência",
)
_INDICADORES_KEYWORDS = (
    "indicador",
    "dashboard",
    "resumo",
    "estatístic",
    "quantas ocorrências",
    "quantas ocorrencias",
    "quantos contêineres",
    "quantos conteineres",
)
_PONTOS_KEYWORDS = (
    "ponto de coleta",
    "pontos de coleta",
    "ponto de descarte",
    "pontos de descarte",
    "descartar",
    "local de descarte",
)
_CONTAINER_KEYWORDS = ("contêiner", "conteiner", "lixeira")
_OCORRENCIA_KEYWORDS = ("ocorrência", "ocorrencia", "protocolo", "status", "andamento")


@dataclass(slots=True)
class ParsedIntent:
    """Resultado da interpretação de uma mensagem."""

    intent: str
    args: dict[str, Any] = field(default_factory=dict)


def _categoria_from_text(texto: str) -> OccurrenceCategory:
    """Mapeia palavras-chave da mensagem para a categoria da ocorrência."""
    minusculo = texto.lower()
    if any(k in minusculo for k in ("transbord", "cheio", "lotado", "overflow")):
        return OccurrenceCategory.OVERFLOW
    if any(k in minusculo for k in ("danificad", "quebrado", "avariado", "danificada")):
        return OccurrenceCategory.DAMAGED_CONTAINER
    if any(k in minusculo for k in ("entulho", "irregular", "descarte", "lixo")):
        return OccurrenceCategory.ILLEGAL_DUMPING
    return OccurrenceCategory.OTHER


def _extract_neighborhood(message: str) -> str | None:
    """Extrai um bairro mencionado após `em`, `no` ou `na`."""
    match = _NEIGHBORHOOD_RE.search(message)
    if not match:
        return None
    return match.group(1).strip(" .,!?;:").title()


def parse(message: str) -> ParsedIntent:
    """Determina a intenção e os argumentos de uma mensagem do usuário."""
    texto = message.strip()
    minusculo = texto.lower()

    # 1. criação de ocorrência tem prioridade (contém verbos de ação claros)
    if any(k in minusculo for k in _CRIAR_KEYWORDS):
        bairro = _extract_neighborhood(texto)
        categoria = _categoria_from_text(texto)
        return ParsedIntent(
            intent=INTENT_CRIAR_OCORRENCIA,
            args={"neighborhood": bairro, "category": categoria, "description": texto},
        )

    # 2. indicadores
    if any(k in minusculo for k in _INDICADORES_KEYWORDS):
        return ParsedIntent(intent=INTENT_CONSULTAR_INDICADORES)

    # 3. pontos de coleta
    if any(k in minusculo for k in _PONTOS_KEYWORDS):
        return ParsedIntent(intent=INTENT_LISTAR_PONTOS)

    # 4. ocorrência por protocolo explícito
    protocolo = _PROTOCOL_RE.search(texto)
    if protocolo:
        return ParsedIntent(
            intent=INTENT_CONSULTAR_OCORRENCIA,
            args={"protocol": protocolo.group(1).upper()},
        )

    # 5. contêiner por código ou palavra-chave
    container = _CONTAINER_RE.search(texto)
    if container:
        return ParsedIntent(
            intent=INTENT_CONSULTAR_CONTAINER,
            args={"code": container.group(1).upper()},
        )
    if any(k in minusculo for k in _CONTAINER_KEYWORDS):
        return ParsedIntent(intent=INTENT_CONSULTAR_CONTAINER)

    # 6. ocorrência sem protocolo (o agente tenta o contexto da sessão)
    if any(k in minusculo for k in _OCORRENCIA_KEYWORDS):
        return ParsedIntent(intent=INTENT_CONSULTAR_OCORRENCIA)

    return ParsedIntent(intent=INTENT_DESCONHECIDA)
