"""Schemas de metadados: valores canônicos dos enums consumidos pelo frontend."""

from __future__ import annotations

from pydantic import BaseModel


class EnumsRead(BaseModel):
    """Todos os valores canônicos do domínio em um único ponto."""

    categories: list[str]
    model_labels: list[str]
    statuses: list[str]
    priorities: list[str]
    alert_levels: list[str]
    user_roles: list[str]
    rpa_statuses: list[str]
    allowed_transitions: dict[str, list[str]]
