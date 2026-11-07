"""Modelos ORM do Smart Clean City (8 entidades do PROJECT_CONTEXT.md §7)."""

from app.models.automation import AgentInteraction, RPAExecution
from app.models.container import Container, SensorReading
from app.models.occurrence import Occurrence, OccurrenceImage, StatusHistory
from app.models.user import User

__all__ = [
    "AgentInteraction",
    "Container",
    "Occurrence",
    "OccurrenceImage",
    "RPAExecution",
    "SensorReading",
    "StatusHistory",
    "User",
]
