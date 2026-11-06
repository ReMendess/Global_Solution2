"""Routers da API REST."""

from app.api.routes import (
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
    "classification",
    "containers",
    "dashboard",
    "health",
    "meta",
    "occurrences",
    "rpa",
    "sensors",
]
