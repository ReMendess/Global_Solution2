"""Schemas de ocorrência: criação, leitura, listagem e mudança de status."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import OccurrenceCategory, OccurrenceStatus, Priority


class OccurrenceCreate(BaseModel):
    """Dados aceitos no registro de uma ocorrência pelo cidadão."""

    neighborhood: str = Field(min_length=3, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    description: str | None = Field(default=None, max_length=1000)
    reporter_name: str | None = Field(default=None, max_length=120)
    reported_category: OccurrenceCategory | None = Field(
        default=None,
        description="Categoria informada pelo cidadão; a IA pode confirmar ou ajustar na FASE 3.",
    )

    @model_validator(mode="after")
    def _validate_coordinates(self) -> OccurrenceCreate:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude e longitude devem ser informadas em conjunto")
        return self


class OccurrenceImageRead(BaseModel):
    """Imagem associada a uma ocorrência."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    file_path: str
    content_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None
    is_simulated: bool
    created_at: datetime


class StatusHistoryRead(BaseModel):
    """Item da trilha de auditoria de status."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    from_status: str | None = None
    to_status: str
    note: str | None = None
    changed_by: str
    created_at: datetime


class OccurrenceRead(BaseModel):
    """Representação pública de uma ocorrência."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    protocol: str
    category: OccurrenceCategory
    status: OccurrenceStatus
    priority: Priority
    description: str | None = None
    neighborhood: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    model_label: str | None = None
    confidence: float | None = None
    needs_human_review: bool
    model_version: str | None = None
    dispatch_protocol: str | None = None
    is_simulated: bool = False
    created_at: datetime
    updated_at: datetime


class OccurrenceDetail(OccurrenceRead):
    """Detalhe administrativo, com imagens e histórico de status."""

    images: list[OccurrenceImageRead] = Field(default_factory=list)
    status_history: list[StatusHistoryRead] = Field(default_factory=list)


class OccurrenceList(BaseModel):
    """Página de ocorrências."""

    items: list[OccurrenceRead]
    total: int
    limit: int
    offset: int


class OccurrenceStatusUpdate(BaseModel):
    """Solicitação de transição de status feita pelo administrador."""

    status: OccurrenceStatus
    note: str | None = Field(default=None, max_length=255)
