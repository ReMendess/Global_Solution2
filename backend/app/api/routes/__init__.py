"""Routers da API REST."""

from app.api.routes import (
    agent,
    classification,
    containers,
    dashboard,
    health,
    meta,
    occurrences,
    rpa,
    sensors,
)

__all__ = [
    "agent",
    "classification",
    "containers",
    "dashboard",
    "health",
    "meta",
    "occurrences",
    "rpa",
    "sensors",
]
