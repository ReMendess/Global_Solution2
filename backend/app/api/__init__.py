"""Camada HTTP: dependências compartilhadas e rotas."""

from app.api.deps import get_current_role, require_admin

__all__ = ["get_current_role", "require_admin"]
