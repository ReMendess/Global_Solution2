"""Ponto único de integração do modelo de visão computacional (MobileNetV2 — FASE 3).

O modelo é carregado sob demanda (lazy), uma única vez por processo, e mantido em
memória. Se os pesos não existirem, `is_model_available()` retorna False e o
restante do sistema continua funcionando: registrar ocorrência nunca depende do
modelo (docs/BUSINESS_RULES.md §6).

Formato esperado dos pesos/metadados: gerados por `python -m ml.src.train`
(ver docs/ML_TRAINING_COLAB.md).
"""

from __future__ import annotations

import io
import json
import logging
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.core.config import PROJECT_ROOT, get_settings

logger = logging.getLogger(__name__)

DEFAULT_CLASSES: tuple[str, str] = ("REGULAR", "IRREGULAR")
FALLBACK_MODEL_VERSION = "unavailable"
DEFAULT_IMAGE_SIZE = 224

_model_lock = threading.Lock()
_cached_model: Any | None = None
_cached_signature: tuple[str, float] | None = None


@dataclass(slots=True)
class ClassificationResult:
    """Saída da inferência sobre uma imagem."""

    label: str
    confidence: float
    model_version: str
    probabilities: dict[str, float] = field(default_factory=dict)
    needs_human_review: bool = False


@dataclass(slots=True)
class ModelInfo:
    """Metadados públicos do modelo (versão, classes e métricas reais)."""

    model_version: str
    classes: list[str]
    image_size: int
    created_at: str | None = None
    architecture: str | None = None
    metrics: dict[str, Any] | None = None
    dataset: dict[str, Any] | None = None
    training: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)


def _resolve(caminho: Path) -> Path:
    """Resolve caminhos relativos a partir da raiz do repositório."""
    return caminho if caminho.is_absolute() else (PROJECT_ROOT / caminho)


def _model_path() -> Path:
    """Caminho absoluto dos pesos."""
    return _resolve(get_settings().model_path)


def _metadata_path() -> Path:
    """Caminho absoluto do JSON de metadados."""
    return _resolve(get_settings().model_metadata_path)


def is_model_available() -> bool:
    """Indica se há pesos treinados publicados (checagem barata, sem importar TF)."""
    return _model_path().is_file()


def load_metadata() -> dict[str, Any] | None:
    """Lê o JSON de metadados gerado no treinamento, se existir."""
    caminho = _metadata_path()
    if not caminho.is_file():
        return None
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Metadados do modelo ilegíveis em %s", caminho, exc_info=True)
        return None


def model_info() -> ModelInfo | None:
    """Monta o resumo público do modelo; None quando não há pesos."""
    if not is_model_available():
        return None

    metadados = load_metadata() or {}
    metricas = metadados.get("metrics")
    return ModelInfo(
        model_version=str(metadados.get("model_version", FALLBACK_MODEL_VERSION)),
        classes=[str(classe) for classe in metadados.get("classes", DEFAULT_CLASSES)],
        image_size=int(metadados.get("image_size", DEFAULT_IMAGE_SIZE)),
        created_at=metadados.get("created_at"),
        architecture=metadados.get("architecture"),
        metrics=metricas if isinstance(metricas, dict) else None,
        dataset=metadados.get("dataset") if isinstance(metadados.get("dataset"), dict) else None,
        training=metadados.get("training") if isinstance(metadados.get("training"), dict) else None,
        warnings=[str(item) for item in metadados.get("warnings") or []],
    )


def require_model_info() -> ModelInfo:
    """Retorna os metadados ou levanta 503 quando o modelo não foi publicado."""
    from app.core.exceptions import ModelUnavailableError

    info = model_info()
    if info is None:
        raise ModelUnavailableError()
    return info


def _signature() -> tuple[str, float] | None:
    """Identifica os pesos atuais (caminho + mtime) para invalidar o cache."""
    caminho = _model_path()
    if not caminho.is_file():
        return None
    return str(caminho), caminho.stat().st_mtime


def _get_model() -> Any | None:
    """Carrega o modelo uma única vez, recarregando se os pesos mudarem."""
    global _cached_model, _cached_signature

    assinatura = _signature()
    if assinatura is None:
        return None

    with _model_lock:
        if _cached_model is not None and _cached_signature == assinatura:
            return _cached_model

        logger.info("Carregando modelo de classificação de %s", assinatura[0])
        import keras  # import tardio: o custo só é pago quando há pesos publicados

        _cached_model = keras.models.load_model(assinatura[0])
        _cached_signature = assinatura
        return _cached_model


def reset_cache() -> None:
    """Descarta o modelo em memória (usado em testes e após publicar novos pesos)."""
    global _cached_model, _cached_signature
    with _model_lock:
        _cached_model = None
        _cached_signature = None


def _build_result(
    probabilidades: list[float], classes: list[str], versao: str
) -> ClassificationResult:
    """Converte o vetor de probabilidades no resultado de domínio."""
    indice = max(range(len(probabilidades)), key=lambda posicao: probabilidades[posicao])
    confidence = float(probabilidades[indice])
    limite = get_settings().confidence_threshold

    return ClassificationResult(
        label=classes[indice] if indice < len(classes) else classes[-1],
        confidence=round(confidence, 4),
        model_version=versao,
        probabilities={
            classe: round(float(probabilidade), 4)
            for classe, probabilidade in zip(classes, probabilidades, strict=False)
        },
        needs_human_review=confidence < limite,
    )


def classify_arrays(array: Any) -> ClassificationResult:
    """Classifica um lote já preparado (shape (1, H, W, 3), pixels em [0, 255])."""
    from app.core.exceptions import ModelUnavailableError

    modelo = _get_model()
    info = model_info()
    if modelo is None or info is None:
        raise ModelUnavailableError()

    probabilidades = modelo.predict(array, verbose=0)[0]
    return _build_result(
        [float(valor) for valor in probabilidades], info.classes, info.model_version
    )


def classify_image(image_path: Path | None) -> ClassificationResult | None:
    """Classifica uma imagem de disco.

    Retorna None (sem levantar erro) quando não há modelo ou quando a inferência
    falha — o fluxo de registro de ocorrência continua normalmente.
    """
    if image_path is None or not is_model_available():
        return None

    try:
        dados = image_path.read_bytes()
        return classify_bytes(dados)
    except Exception:  # noqa: BLE001 - falha de inferência nunca bloqueia o registro
        logger.exception("Falha ao classificar a imagem %s", image_path)
        return None


def classify_bytes(data: bytes) -> ClassificationResult:
    """Classifica uma imagem em memória (usado pela rota de diagnóstico).

    Diferente de `classify_image`, propaga o erro de modelo indisponível (503) e
    sinaliza imagem ilegível, porque aqui a requisição é explicitamente de inferência.
    """
    import numpy as np
    from PIL import Image

    from app.core.exceptions import UnprocessableError

    info = require_model_info()

    try:
        with Image.open(io.BytesIO(data)) as imagem:
            rgb = imagem.convert("RGB")
            redimensionada = rgb.resize((info.image_size, info.image_size), Image.LANCZOS)
            array = np.asarray(redimensionada, dtype="float32")
    except Exception as exc:  # noqa: BLE001 - arquivo corrompido ou formato inválido
        raise UnprocessableError("Não foi possível ler a imagem enviada.") from exc

    return classify_arrays(np.expand_dims(array, axis=0))
