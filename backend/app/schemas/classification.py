"""Schemas das rotas de classificação por visão computacional."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ClassificationRead(BaseModel):
    """Resultado de uma classificação isolada de imagem."""

    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    probabilities: dict[str, float] = Field(default_factory=dict)
    model_version: str
    needs_human_review: bool


class ModelMetricsRead(BaseModel):
    """Métricas reais obtidas na avaliação do conjunto de teste."""

    accuracy: float | None = None
    precision_weighted: float | None = None
    recall_weighted: float | None = None
    f1_weighted: float | None = None
    precision_macro: float | None = None
    recall_macro: float | None = None
    f1_macro: float | None = None
    confusion_matrix: list[list[int]] | None = None
    classes: list[str] | None = None
    per_class: dict[str, dict[str, float | int]] | None = None
    support_total: int | None = None
    meets_minimum_accuracy: bool | None = None


class ModelInfoRead(BaseModel):
    """Informações públicas do modelo publicado (versão, classes e métricas)."""

    model_version: str
    classes: list[str]
    image_size: int
    architecture: str | None = None
    created_at: str | None = None
    metrics: ModelMetricsRead | None = None
    dataset: dict | None = None
    training: dict | None = None
    warnings: list[str] = Field(default_factory=list)
