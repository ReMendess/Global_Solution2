"""Cálculo das métricas de avaliação e gravação do relatório.

Usa scikit-learn para accuracy, precision, recall, F1 e matriz de confusão,
conforme exigido em docs/PROJECT_CONTEXT.md §8.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ml.src.config import CLASSES, MIN_ACCEPTABLE_ACCURACY, REPORTS_DIR

if TYPE_CHECKING:  # pragma: no cover - apenas tipagem
    pass


def predict_dataset(model, dataset) -> tuple[np.ndarray, np.ndarray]:
    """Executa a inferência sobre um dataset e devolve (rótulos reais, previstos)."""
    probabilidades = model.predict(dataset, verbose=0)
    reais = np.concatenate([y.numpy() for _, y in dataset], axis=0)
    return np.argmax(reais, axis=1), np.argmax(probabilidades, axis=1)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, object]:
    """Calcula as métricas obrigatórias do projeto a partir dos rótulos."""
    labels = list(range(len(CLASSES)))
    matriz = confusion_matrix(y_true, y_pred, labels=labels)
    relatorio = classification_report(
        y_true,
        y_pred,
        labels=labels,
        target_names=list(CLASSES),
        output_dict=True,
        zero_division=0,
    )

    acuracia = float(accuracy_score(y_true, y_pred))
    return {
        "accuracy": round(acuracia, 4),
        "precision_weighted": round(
            float(
                precision_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)
            ),
            4,
        ),
        "recall_weighted": round(
            float(recall_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)),
            4,
        ),
        "f1_weighted": round(
            float(f1_score(y_true, y_pred, labels=labels, average="weighted", zero_division=0)), 4
        ),
        "precision_macro": round(
            float(precision_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)),
            4,
        ),
        "recall_macro": round(
            float(recall_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)), 4
        ),
        "f1_macro": round(
            float(f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)), 4
        ),
        "confusion_matrix": matriz.tolist(),
        "classes": list(CLASSES),
        "per_class": {
            classe: {
                "precision": round(float(relatorio[classe]["precision"]), 4),
                "recall": round(float(relatorio[classe]["recall"]), 4),
                "f1_score": round(float(relatorio[classe]["f1-score"]), 4),
                "support": int(relatorio[classe]["support"]),
            }
            for classe in CLASSES
        },
        "support_total": int(relatorio["macro avg"]["support"]),
        "meets_minimum_accuracy": bool(acuracia >= MIN_ACCEPTABLE_ACCURACY),
    }


def plot_confusion_matrix(
    metrics: dict[str, object], output_path: Path | None = None
) -> Path | None:
    """Salva a matriz de confusão como imagem PNG (Figura do relatório)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import seaborn as sns

    matriz = np.array(metrics["confusion_matrix"], dtype=int)
    destino = output_path or (REPORTS_DIR / "matriz_confusao.png")
    destino.parent.mkdir(parents=True, exist_ok=True)

    figura, eixo = plt.subplots(figsize=(5, 4.2))
    sns.heatmap(
        matriz,
        annot=True,
        fmt="d",
        cmap="Greens",
        cbar=False,
        xticklabels=list(CLASSES),
        yticklabels=list(CLASSES),
        ax=eixo,
    )
    eixo.set_xlabel("Previsto")
    eixo.set_ylabel("Real")
    eixo.set_title(f"Matriz de confusão — accuracy {metrics['accuracy']:.2%}")
    figura.tight_layout()
    figura.savefig(destino, dpi=150)
    plt.close(figura)
    return destino


def write_report(report: dict[str, object], output_path: Path | None = None) -> Path:
    """Grava o relatório de treinamento/avaliação em JSON."""
    destino = output_path or (REPORTS_DIR / "relatorio_treinamento.json")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return destino


def evaluate_saved_model(
    model_path: Path | None = None,
    processed_dir: Path | None = None,
    batch_size: int = 32,
) -> dict[str, object]:
    """Reavalia um modelo já treinado sobre a divisão de teste em disco."""
    import keras

    from ml.src.config import BATCH_SIZE, MODEL_PATH, PROCESSED_DIR
    from ml.src.preprocess import build_datasets

    caminho = model_path or MODEL_PATH
    if not caminho.exists():
        raise FileNotFoundError(
            f"Modelo não encontrado em {caminho}. Treine primeiro (python -m ml.src.train)."
        )

    modelo = keras.models.load_model(caminho)
    _, _, teste = build_datasets(
        processed_dir or PROCESSED_DIR, batch_size=batch_size or BATCH_SIZE
    )
    y_true, y_pred = predict_dataset(modelo, teste)
    metricas = compute_metrics(y_true, y_pred)

    plot_confusion_matrix(metricas)
    write_report({"model_path": str(caminho), "metrics": metricas})
    return metricas


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada: `python -m ml.src.evaluate`."""
    import argparse

    parser = argparse.ArgumentParser(description="Reavalia o modelo treinado no conjunto de teste.")
    parser.add_argument("--model-path", type=Path, default=None)
    parser.add_argument("--processed-dir", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args(argv)

    metricas = evaluate_saved_model(args.model_path, args.processed_dir, args.batch_size)
    print(json.dumps(metricas, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
