"""Schemas do agente conversacional (mensagens e histórico de sessão)."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentMessageCreate(BaseModel):
    """Mensagem enviada pelo usuário ao agente."""

    session_id: str = Field(min_length=3, max_length=64)
    message: str = Field(min_length=1, max_length=1000)


class AgentMessageRead(BaseModel):
    """Resposta do agente a uma mensagem."""

    session_id: str
    intent: str
    tool_used: str | None = None
    response: str
    data: dict | None = None


class AgentInteractionRead(BaseModel):
    """Item do histórico de conversa (pergunta + resposta do agente)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    intent: str
    message: str
    response: str
    tool_used: str | None = None
    tool_payload: str | None = None
    created_at: datetime


class AgentSessionRead(BaseModel):
    """Histórico completo de uma sessão."""

    session_id: str
    interactions: list[AgentInteractionRead] = Field(default_factory=list)
    total: int = 0
