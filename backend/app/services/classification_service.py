"""Ponto único de integração do modelo de visão computacional.

Na FASE 1 não existe modelo treinado, então `is_model_available()` retorna False e
`classify_image()` retorna None. A FASE 3 substitui a implementação interna por inferência
real com MobileNetV2, mantendo esta interface — por isso o restante do backend não muda.

Regra de negócio respeitada aqui: ausência/falha do modelo nunca impede o registro de uma
ocorrência (docs/BUSINESS_RULES.md §6).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.core.config import get_settings

if TYPE_CHECKING:
    from pathlib import Path

MODEL_VERSION_PLACEHOLDER = "unavailable"


@dataclass(slots=True)
class ClassificationResult:
    """Saída da inferência sobre uma imagem."""

    label: str
    confidence: float
    model_version: str


def is_model_available() -> bool:
    """Indica se há pesos treinados disponíveis para inferência."""
    settings = get_settings()
    return settings.model_path.exists()


def classify_image(image_path: Path | None) -> ClassificationResult | None:
    """Classifica uma imagem; retorna None enquanto o modelo não existir (FASE 3)."""
    if image_path is None or not is_model_available():
        return None
    # A inferência real (MobileNetV2) é implementada na FASE 3.
    return None
