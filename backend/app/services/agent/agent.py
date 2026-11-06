"""Orquestração do agente conversacional.

Fluxo: mensagem → interpretação de intenções → ferramenta (com contexto da
sessão) → resposta + persistência da interação. Nenhuma informação é inventada:
as ferramentas leem serviços reais e, quando não há dado, o agente pede os dados
que faltam ou responde "não encontrado".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import OccurrenceCategory
from app.models.automation import AgentInteraction
from app.services.agent import tools
from app.services.agent.intent_parser import (
    INTENT_CONSULTAR_CONTAINER,
    INTENT_CONSULTAR_INDICADORES,
    INTENT_CONSULTAR_OCORRENCIA,
    INTENT_CRIAR_OCORRENCIA,
    INTENT_DESCONHECIDA,
    INTENT_LISTAR_PONTOS,
    parse,
)
from app.services.agent.session import SessionStore, session_store

ORIENTATION = (
    "Não entendi. Você pode perguntar, por exemplo: "
    '"status da ocorrência CL-2026-000012", "nível do contêiner CONT-001", '
    '"pontos de coleta" ou "indicadores".'
)


@dataclass(slots=True)
class AgentReply:
    """Resposta pronta para ser serializada pela rota."""

    session_id: str
    intent: str
    tool_used: str | None
    response: str
    data: dict[str, Any] | None = None


def _persist(
    db: Session,
    session_id: str,
    user_id: int | None,
    message: str,
    reply: AgentReply,
) -> None:
    """Grava a interação no histórico (auditoria)."""
    db.add(
        AgentInteraction(
            session_id=session_id,
            user_id=user_id,
            intent=reply.intent,
            message=message,
            response=reply.response,
            tool_used=reply.tool_used,
            tool_payload=json.dumps(reply.data, ensure_ascii=False, default=str)
            if reply.data
            else None,
        )
    )
    db.commit()


def handle_message(
    db: Session,
    session_id: str,
    message: str,
    *,
    user_id: int | None = None,
    store: SessionStore | None = None,
) -> AgentReply:
    """Processa uma mensagem e devolve a resposta do agente."""
    contexto = (store or session_store).get(session_id)
    parsed = parse(message)

    if parsed.intent == INTENT_CONSULTAR_OCORRENCIA:
        protocolo = parsed.args.get("protocol") or contexto.last_protocol
        if not protocolo:
            reply = AgentReply(
                session_id,
                parsed.intent,
                None,
                "Informe o protocolo da ocorrência, por exemplo: CL-2026-000012.",
            )
        else:
            resultado = tools.consultar_ocorrencia(db, protocolo)
            (store or session_store).remember_protocol(session_id, protocolo)
            reply = AgentReply(
                session_id,
                parsed.intent,
                "consultar_ocorrencia",
                resultado.response,
                resultado.data,
            )

    elif parsed.intent == INTENT_CONSULTAR_CONTAINER:
        codigo = parsed.args.get("code") or contexto.last_container
        if not codigo:
            reply = AgentReply(
                session_id,
                parsed.intent,
                None,
                "Informe o código do contêiner, por exemplo: CONT-001.",
            )
        else:
            resultado = tools.consultar_container(db, codigo)
            (store or session_store).remember_container(session_id, codigo)
            reply = AgentReply(
                session_id,
                parsed.intent,
                "consultar_container",
                resultado.response,
                resultado.data,
            )

    elif parsed.intent == INTENT_LISTAR_PONTOS:
        resultado = tools.listar_pontos_coleta(db)
        reply = AgentReply(
            session_id, parsed.intent, "listar_pontos_coleta", resultado.response, resultado.data
        )

    elif parsed.intent == INTENT_CONSULTAR_INDICADORES:
        resultado = tools.consultar_indicadores(db)
        reply = AgentReply(
            session_id, parsed.intent, "consultar_indicadores", resultado.response, resultado.data
        )

    elif parsed.intent == INTENT_CRIAR_OCORRENCIA:
        bairro = parsed.args.get("neighborhood")
        if not bairro:
            reply = AgentReply(
                session_id,
                parsed.intent,
                None,
                'Em qual bairro? Informe, por exemplo: "registrar ocorrência em Pinheiros".',
            )
        else:
            categoria = parsed.args["category"]
            if not isinstance(categoria, OccurrenceCategory):
                categoria = OccurrenceCategory(categoria)
            resultado = tools.criar_ocorrencia(
                db,
                neighborhood=bairro,
                category=categoria,
                description=parsed.args.get("description"),
            )
            if resultado.data:
                (store or session_store).remember_protocol(session_id, resultado.data["protocol"])
            reply = AgentReply(
                session_id, parsed.intent, "criar_ocorrencia", resultado.response, resultado.data
            )

    else:
        reply = AgentReply(session_id, INTENT_DESCONHECIDA, None, ORIENTATION, None)

    _persist(db, session_id, user_id, message, reply)
    return reply
