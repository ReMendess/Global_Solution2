"""Schemas Pydantic de entrada e saída da API."""

from app.schemas.agent import (
    AgentInteractionRead,
    AgentMessageCreate,
    AgentMessageRead,
    AgentSessionRead,
)
from app.schemas.classification import (
    ClassificationRead,
    ModelInfoRead,
    ModelMetricsRead,
)
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
from app.schemas.rpa import (
    RPAExecutionCreate,
    RPAExecutionList,
    RPAExecutionRead,
    RPAQueueItem,
    RPAQueueList,
)

__all__ = [
    "AgentInteractionRead",
    "AgentMessageCreate",
    "AgentMessageRead",
    "AgentSessionRead",
    "ClassificationRead",
    "ContainerAlertSummary",
    "ContainerList",
    "ContainerRead",
    "DashboardSummary",
    "EnumsRead",
    "ModelInfoRead",
    "ModelMetricsRead",
    "NeighborhoodRanking",
    "OccurrenceCreate",
    "OccurrenceDetail",
    "OccurrenceImageRead",
    "OccurrenceList",
    "OccurrenceRead",
    "OccurrenceStatusUpdate",
    "RPAExecutionCreate",
    "RPAExecutionList",
    "RPAExecutionRead",
    "RPAQueueItem",
    "RPAQueueList",
    "SensorReadingCreate",
    "SensorReadingList",
    "SensorReadingRead",
    "StatusHistoryRead",
]
