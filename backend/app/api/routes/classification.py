"""Rotas de classificação por visão computacional (FASE 3)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, File, UploadFile

from app.core.config import get_settings
from app.core.constants import ALLOWED_IMAGE_TYPES
from app.core.exceptions import PayloadTooLargeError, UnprocessableError
from app.schemas.classification import ClassificationRead, ModelInfoRead
from app.services import classification_service

router = APIRouter(prefix="/api/v1/classification", tags=["classificação"])


@router.get(
    "/model-info",
    response_model=ModelInfoRead,
    summary="Versão, classes e métricas reais do modelo",
)
def get_model_info() -> ModelInfoRead:
    """Retorna os metadados gerados no treinamento (503 se não houver modelo)."""
    info = classification_service.require_model_info()
    return ModelInfoRead(
        model_version=info.model_version,
        classes=info.classes,
        image_size=info.image_size,
        architecture=info.architecture,
        created_at=info.created_at,
        metrics=info.metrics,  # type: ignore[arg-type]
        dataset=info.dataset,
        training=info.training,
        warnings=info.warnings,
    )


@router.post(
    "/predict",
    response_model=ClassificationRead,
    summary="Classifica uma imagem isolada (não persiste ocorrência)",
)
def predict(
    image: Annotated[UploadFile, File(description="Imagem JPEG ou PNG")],
) -> ClassificationRead:
    """Executa a inferência sobre a imagem enviada e devolve as probabilidades.

    Não grava nada no banco: é uma rota de diagnóstico do modelo. O registro de
    ocorrência tem seu próprio fluxo resiliente (ver `occurrence_service`).
    """
    settings = get_settings()
    content_type = image.content_type or ""
    if content_type not in ALLOWED_IMAGE_TYPES:
        permitidos = ", ".join(sorted(ALLOWED_IMAGE_TYPES))
        raise UnprocessableError(f"Formato de imagem não suportado. Use: {permitidos}.")

    dados = image.file.read(settings.max_upload_bytes + 1)
    if not dados:
        raise UnprocessableError("O arquivo de imagem está vazio.")
    if len(dados) > settings.max_upload_bytes:
        raise PayloadTooLargeError(f"A imagem excede o limite de {settings.max_upload_mb} MB.")

    resultado = classification_service.classify_bytes(dados)
    return ClassificationRead(
        label=resultado.label,
        confidence=resultado.confidence,
        probabilities=resultado.probabilities,
        model_version=resultado.model_version,
        needs_human_review=resultado.needs_human_review,
    )
