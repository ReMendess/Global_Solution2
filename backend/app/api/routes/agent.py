"""Rotas do agente conversacional."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.automation import AgentInteraction
from app.schemas.agent import (
    AgentInteractionRead,
    AgentMessageCreate,
    AgentMessageRead,
    AgentSessionRead,
)
from app.services.agent.agent import handle_message

router = APIRouter(prefix="/api/v1/agent", tags=["agente"])


@router.post(
    "/messages",
    response_model=AgentMessageRead,
    summary="Envia uma mensagem e recebe a resposta do agente",
)
def send_message(
    payload: AgentMessageCreate,
    db: Session = Depends(get_db),
) -> AgentMessageRead:
    """Interpreta a intenção e executa a ferramenta correspondente sobre dados reais."""
    resposta = handle_message(db, payload.session_id, payload.message)
    return AgentMessageRead(
        session_id=resposta.session_id,
        intent=resposta.intent,
        tool_used=resposta.tool_used,
        response=resposta.response,
        data=resposta.data,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=AgentSessionRead,
    summary="Histórico de uma sessão de conversa",
)
def get_session(
    session_id: str,
    db: Session = Depends(get_db),
) -> AgentSessionRead:
    """Retorna as interações persistidas da sessão, em ordem cronológica."""
    interacoes = (
        db.execute(
            select(AgentInteraction)
            .where(AgentInteraction.session_id == session_id)
            .order_by(AgentInteraction.created_at.asc(), AgentInteraction.id.asc())
        )
        .scalars()
        .all()
    )
    return AgentSessionRead(
        session_id=session_id,
        interactions=[AgentInteractionRead.model_validate(item) for item in interacoes],
        total=len(interacoes),
    )
