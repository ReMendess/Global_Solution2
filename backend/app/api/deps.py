"""Dependências de acesso e perfil (controle demonstrativo, revisado na FASE 7)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header

from app.core.enums import UserRole
from app.core.exceptions import ForbiddenError

ROLE_HEADER = "X-User-Role"


def get_current_role(
    x_user_role: Annotated[str | None, Header(alias=ROLE_HEADER)] = None,
) -> UserRole:
    """Lê o perfil do cabeçalho `X-User-Role` (padrão: cidadão)."""
    if not x_user_role:
        return UserRole.CITIZEN
    try:
        return UserRole(x_user_role.strip().upper())
    except ValueError as exc:
        raise ForbiddenError(f"Perfil inválido no cabeçalho {ROLE_HEADER}.") from exc


def require_admin(
    role: Annotated[UserRole, Depends(get_current_role)],
) -> UserRole:
    """Garante que a requisição vem do perfil administrador."""
    if role is not UserRole.ADMIN:
        raise ForbiddenError("Operação disponível apenas para o perfil ADMIN.")
    return role
