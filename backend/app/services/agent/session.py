"""Contexto simples por sessão (em memória).

Guarda a última ocorrência/contêiner citado para permitir perguntas de
continuidade ("e o status dele?"). Em memória por simplicidade: o contexto é
perdido ao reiniciar o processo — limitação documentada na FASE 6.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass


@dataclass(slots=True)
class SessionContext:
    """Estado de uma sessão de conversa."""

    last_protocol: str | None = None
    last_container: str | None = None


class SessionStore:
    """Armazena o contexto de várias sessões com acesso thread-safe."""

    def __init__(self) -> None:
        self._sessoes: dict[str, SessionContext] = {}
        self._lock = threading.Lock()

    def get(self, session_id: str) -> SessionContext:
        with self._lock:
            return self._sessoes.setdefault(session_id, SessionContext())

    def remember_protocol(self, session_id: str, protocol: str) -> None:
        with self._lock:
            self._sessoes.setdefault(session_id, SessionContext()).last_protocol = protocol

    def remember_container(self, session_id: str, code: str) -> None:
        with self._lock:
            self._sessoes.setdefault(session_id, SessionContext()).last_container = code

    def clear(self) -> None:
        with self._lock:
            self._sessoes.clear()


# Instância única usada pelo agente (uma por processo).
session_store = SessionStore()
