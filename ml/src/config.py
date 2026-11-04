"""Constantes compartilhadas pelo pipeline de treinamento e pela avaliação."""

from __future__ import annotations

from pathlib import Path

# ml/src/config.py -> parents[0]=src, [1]=ml, [2]=raiz do repositório.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = PROJECT_ROOT / "ml"

RAW_DIR = ML_ROOT / "data" / "raw"
PROCESSED_DIR = ML_ROOT / "data" / "processed"
MODELS_DIR = ML_ROOT / "models"
REPORTS_DIR = ML_ROOT / "reports"

# --- modelo ---
MODEL_VERSION = "mobilenetv2-v1"
MODEL_FILENAME = "cidade_limpa_mobilenetv2.keras"
METADATA_FILENAME = "cidade_limpa_mobilenetv2.metadata.json"
REPORT_FILENAME = "relatorio_treinamento.json"
CONFUSION_MATRIX_FILENAME = "matriz_confusao.png"
TRAINING_CURVES_FILENAME = "curvas_treinamento.png"

MODEL_PATH = MODELS_DIR / MODEL_FILENAME
METADATA_PATH = MODELS_DIR / METADATA_FILENAME
REPORT_PATH = REPORTS_DIR / REPORT_FILENAME

# --- classes (ordem fixa: o índice 0 é REGULAR e o 1 é IRREGULAR) ---
CLASSES: tuple[str, str] = ("REGULAR", "IRREGULAR")
REGULAR_INDEX = 0
IRREGULAR_INDEX = 1

# --- entrada ---
IMAGE_SIZE = 224  # tamanho nativo do MobileNetV2
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".bmp"})
RESCALE_SCALE = 1.0 / 127.5
RESCALE_OFFSET = -1.0  # MobileNetV2 espera entradas em [-1, 1]

# --- divisão do dataset ---
SEED = 42
SPLITS: dict[str, float] = {"train": 0.70, "val": 0.15, "test": 0.15}

# --- hiperparâmetros padrão ---
BATCH_SIZE = 32
EPOCHS_HEAD = 10  # etapa 1: base congelada
EPOCHS_FINETUNE = 6  # etapa 2: ajuste fino
LEARNING_RATE_HEAD = 1e-3
LEARNING_RATE_FINETUNE = 1e-5
DROPOUT = 0.3
UNFREEZE_LAYERS = 30  # últimas camadas do MobileNetV2 liberadas no ajuste fino

# --- qualidade mínima aceitável (usada apenas como alerta no relatório) ---
MIN_ACCEPTABLE_ACCURACY = 0.75


class DatasetError(RuntimeError):
    """Erro de preparação do dataset, com mensagem orientativa em pt-BR."""


def describe_paths() -> dict[str, str]:
    """Retorna os caminhos usados pelo pipeline (útil no notebook e nos logs)."""
    return {
        "raw": str(RAW_DIR),
        "processed": str(PROCESSED_DIR),
        "models": str(MODELS_DIR),
        "reports": str(REPORTS_DIR),
        "model_file": str(MODEL_PATH),
        "metadata_file": str(METADATA_PATH),
    }
