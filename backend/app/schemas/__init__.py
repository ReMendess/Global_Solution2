"""Schemas Pydantic de entrada e saída da API."""

from app.schemas.container import (
    ContainerList,
    ContainerRead,
    SensorReadingCreate,
    SensorReadingList,
    SensorReadingRead,
)
from app.schemas.dashboard import (
    ContainerAlertSummary,
    DashboardSummary,
    NeighborhoodRanking,
)
from app.schemas.meta import EnumsRead
from app.schemas.occurrence import (
    OccurrenceCreate,
    OccurrenceDetail,
    OccurrenceImageRead,
    OccurrenceList,
    OccurrenceRead,
    OccurrenceStatusUpdate,
    StatusHistoryRead,
)

__all__ = [
    "ContainerAlertSummary",
    "ContainerList",
    "ContainerRead",
    "DashboardSummary",
    "EnumsRead",
    "NeighborhoodRanking",
    "OccurrenceCreate",
    "OccurrenceDetail",
    "OccurrenceImageRead",
    "OccurrenceList",
    "OccurrenceRead",
    "OccurrenceStatusUpdate",
    "SensorReadingCreate",
    "SensorReadingList",
    "SensorReadingRead",
    "StatusHistoryRead",
]
