"""Treinamento do classificador REGULAR/IRREGULAR (MobileNetV2 + transfer learning).

Execução local (a oficial acontece no Google Colab — ver docs/ML_TRAINING_COLAB.md):

    python -m ml.src.train --epochs-head 10 --epochs-finetune 6

Fluxo:
1. valida o dataset bruto (`ml/data/raw/REGULAR` e `ml/data/raw/IRREGULAR`);
2. divide em treino/validação/teste de forma reprodutível;
3. treina a cabeça com a base MobileNetV2 congelada;
4. ajusta finamente as últimas camadas da base;
5. avalia no conjunto de teste e grava pesos + metadados + relatório.
"""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import UTC, datetime
from pathlib import Path

from ml.src import dataset as dataset_module
from ml.src import evaluate as evaluate_module
from ml.src.config import (
    BATCH_SIZE,
    CLASSES,
    CONFUSION_MATRIX_FILENAME,
    EPOCHS_FINETUNE,
    EPOCHS_HEAD,
    IMAGE_SIZE,
    LEARNING_RATE_FINETUNE,
    LEARNING_RATE_HEAD,
    METADATA_PATH,
    MODEL_PATH,
    MODEL_VERSION,
    PROCESSED_DIR,
    RAW_DIR,
    REPORTS_DIR,
    SEED,
    TRAINING_CURVES_FILENAME,
    UNFREEZE_LAYERS,
)
from ml.src.model import build_model, unfreeze_top_layers
from ml.src.preprocess import build_augmentation, build_datasets


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Lê os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Treina o modelo Smart Clean City (MobileNetV2).")
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR, help="dataset bruto")
    parser.add_argument(
        "--processed-dir", type=Path, default=PROCESSED_DIR, help="dataset dividido"
    )
    parser.add_argument("--epochs-head", type=int, default=EPOCHS_HEAD, help="épocas da etapa 1")
    parser.add_argument(
        "--epochs-finetune", type=int, default=EPOCHS_FINETUNE, help="épocas do ajuste fino"
    )
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument(
        "--unfreeze-layers", type=int, default=UNFREEZE_LAYERS, help="camadas liberadas no ajuste"
    )
    parser.add_argument("--skip-split", action="store_true", help="reutiliza o dataset já dividido")
    parser.add_argument("--model-path", type=Path, default=MODEL_PATH)
    parser.add_argument("--metadata-path", type=Path, default=METADATA_PATH)
    return parser.parse_args(argv)


def _callbacks(monitor: str = "val_accuracy", checkpoint: Path | None = None):
    """Callbacks padrão: parada antecipada, redução do LR e melhor checkpoint."""
    import keras

    lista = [
        keras.callbacks.EarlyStopping(monitor=monitor, patience=4, restore_best_weights=True),
        keras.callbacks.ReduceLROnPlateau(monitor=monitor, factor=0.5, patience=2, min_lr=1e-6),
    ]
    if checkpoint is not None:
        checkpoint.parent.mkdir(parents=True, exist_ok=True)
        lista.append(
            keras.callbacks.ModelCheckpoint(
                filepath=str(checkpoint), monitor=monitor, save_best_only=True, verbose=0
            )
        )
    return lista


def _plot_curves(history_head: dict, history_finetune: dict, destino: Path) -> Path:
    """Salva as curvas de accuracy/loss das duas etapas de treinamento."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    def _concat(chave: str) -> list[float]:
        return list(history_head.get(chave, [])) + list(history_finetune.get(chave, []))

    epocas = range(1, len(_concat("accuracy")) + 1)
    figura, eixos = plt.subplots(1, 2, figsize=(11, 4))
    eixos[0].plot(epocas, _concat("accuracy"), label="treino")
    eixos[0].plot(epocas, _concat("val_accuracy"), label="validação")
    eixos[0].set_title("Accuracy por época")
    eixos[0].set_xlabel("época")
    eixos[0].legend()

    eixos[1].plot(epocas, _concat("loss"), label="treino")
    eixos[1].plot(epocas, _concat("val_loss"), label="validação")
    eixos[1].set_title("Loss por época")
    eixos[1].set_xlabel("época")
    eixos[1].legend()

    figura.tight_layout()
    destino.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(destino, dpi=150)
    plt.close(figura)
    return destino


def run(args: argparse.Namespace) -> dict[str, object]:
    """Executa o pipeline completo e devolve o relatório gerado."""
    import keras
    import tensorflow as tf

    inicio = time.perf_counter()
    avisos: list[str] = []

    # 1. dataset
    resumo = dataset_module.discover(args.raw_dir)
    avisos.extend(dataset_module.warnings_for(resumo))
    print(f"Dataset: {resumo.as_dict()}")

    if args.skip_split:
        manifesto: dict[str, object] = {"source_counts": dict(resumo.counts), "reused": True}
    else:
        manifesto = dataset_module.split_dataset(
            raw_dir=args.raw_dir,
            processed_dir=args.processed_dir,
            seed=args.seed,
        )
        print(f"Divisão: {manifesto['by_split']}")

    # 2. datasets do TensorFlow
    treino, validacao, teste = build_datasets(
        args.processed_dir, batch_size=args.batch_size, image_size=IMAGE_SIZE, seed=args.seed
    )
    aumento = build_augmentation()
    treino = treino.map(lambda x, y: (aumento(x, training=True), y)).prefetch(8)

    # 3. etapa 1 — cabeça com base congelada
    modelo = build_model(image_size=IMAGE_SIZE, learning_rate=LEARNING_RATE_HEAD)
    print(f"Parâmetros totais: {modelo.count_params():,}")

    historico_cabeca = modelo.fit(
        treino,
        validation_data=validacao,
        epochs=args.epochs_head,
        callbacks=_callbacks(),
        verbose=2,
    ).history

    # 4. etapa 2 — ajuste fino das últimas camadas
    liberadas = unfreeze_top_layers(
        modelo, num_layers=args.unfreeze_layers, learning_rate=LEARNING_RATE_FINETUNE
    )
    print(f"Camadas liberadas para ajuste fino: {liberadas}")

    historico_ajuste = modelo.fit(
        treino,
        validation_data=validacao,
        epochs=args.epochs_finetune,
        callbacks=_callbacks(),
        verbose=2,
    ).history

    # 5. avaliação no conjunto de teste (nunca visto no treino)
    y_true, y_pred = evaluate_module.predict_dataset(modelo, teste)
    metricas = evaluate_module.compute_metrics(y_true, y_pred)
    print(f"Métricas de teste: {json.dumps(metricas, ensure_ascii=False)}")

    # 6. artefatos
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    modelo.save(args.model_path)

    matriz_path = evaluate_module.plot_confusion_matrix(
        metricas, REPORTS_DIR / CONFUSION_MATRIX_FILENAME
    )
    curvas_path = _plot_curves(
        historico_cabeca, historico_ajuste, REPORTS_DIR / TRAINING_CURVES_FILENAME
    )

    relatorio: dict[str, object] = {
        "model_version": MODEL_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "architecture": "MobileNetV2 (ImageNet) + transfer learning",
        "classes": list(CLASSES),
        "image_size": IMAGE_SIZE,
        "input_range": "[0, 255] — normalização para [-1, 1] dentro do modelo",
        "dataset": {"source": resumo.as_dict(), "split": manifesto},
        "training": {
            "epochs_head": args.epochs_head,
            "epochs_finetune": args.epochs_finetune,
            "batch_size": args.batch_size,
            "seed": args.seed,
            "learning_rate_head": LEARNING_RATE_HEAD,
            "learning_rate_finetune": LEARNING_RATE_FINETUNE,
            "unfrozen_layers": liberadas,
            "history_head": historico_cabeca,
            "history_finetune": historico_ajuste,
            "duration_seconds": round(time.perf_counter() - inicio, 1),
            "tensorflow_version": tf.__version__,
            "keras_version": keras.__version__,
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "metrics": metricas,
        "reports": {
            "confusion_matrix": str(matriz_path) if matriz_path else None,
            "training_curves": str(curvas_path),
        },
        "warnings": avisos,
    }

    evaluate_module.write_report(relatorio, REPORTS_DIR / "relatorio_treinamento.json")

    metadados: dict[str, object] = {
        "model_version": MODEL_VERSION,
        "created_at": relatorio["created_at"],
        "architecture": relatorio["architecture"],
        "classes": list(CLASSES),
        "image_size": IMAGE_SIZE,
        "input_range": relatorio["input_range"],
        "metrics": metricas,
        "dataset": relatorio["dataset"],
        "training": {
            chave: relatorio["training"][chave]  # type: ignore[index]
            for chave in (
                "epochs_head",
                "epochs_finetune",
                "batch_size",
                "seed",
                "duration_seconds",
                "tensorflow_version",
                "keras_version",
            )
        },
        "warnings": avisos,
    }
    args.metadata_path.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_path.write_text(
        json.dumps(metadados, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Modelo salvo em: {args.model_path}")
    print(f"Metadados salvos em: {args.metadata_path}")
    print(f"Duração total: {relatorio['training']['duration_seconds']}s")  # type: ignore[index]
    return relatorio


def main(argv: list[str] | None = None) -> None:
    """Ponto de entrada da linha de comando."""
    run(parse_args(argv))


if __name__ == "__main__":
    main()
