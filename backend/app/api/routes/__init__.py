"""Routers da API REST."""

from app.api.routes import containers, dashboard, health, meta, occurrences, sensors

__all__ = ["containers", "dashboard", "health", "meta", "occurrences", "sensors"]
