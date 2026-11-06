"""Seletores CSS do portal administrativo fictício.

Centralizados aqui para que o robô e os testes usem a mesma fonte de verdade.
"""

from __future__ import annotations

SELECTORS: dict[str, str] = {
    "protocol": "#protocol",
    "category": "#category",
    "priority": "#priority",
    "neighborhood": "#neighborhood",
    "address": "#address",
    "description": "#description",
    "submit": "#submit-button",
    "protocol_result": "#portal-protocol",
}

# Campos do formulário, na ordem em que devem ser preenchidos.
FORM_FIELDS: tuple[str, ...] = (
    "protocol",
    "category",
    "priority",
    "neighborhood",
    "address",
    "description",
)
