"""Carregamento, normalização e aumento de dados das imagens.

Mantém uma única definição do pré-processamento para treino, avaliação e
inferência no backend — evitando divergência entre treino e produção.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from ml.src.config import CLASSES, IMAGE_SIZE, RESCALE_OFFSET, RESCALE_SCALE

if TYPE_CHECKING:  # pragma: no cover - apenas tipagem
    pass


def load_image_array(path: Path, image_size: int = IMAGE_SIZE) -> np.ndarray:
    """Lê uma imagem de disco e devolve um array float32 com shape (1, H, W, 3).

    Usa Pillow (RGB + redimensionamento Lanczos) e mantém os pixels em [0, 255],
    porque a normalização para [-1, 1] acontece dentro do modelo.
    """
    from PIL import Image

    with Image.open(path) as imagem:
        rgb = imagem.convert("RGB")
        redimensionada = rgb.resize((image_size, image_size), Image.LANCZOS)
        array = np.asarray(redimensionada, dtype="float32")
    return np.expand_dims(array, axis=0)


def normalize(array: np.ndarray) -> np.ndarray:
    """Aplica a mesma escala usada pelas camadas do modelo ([-1, 1])."""
    return array * RESCALE_SCALE + RESCALE_OFFSET


def build_augmentation():
    """Bloco de aumento de dados aplicado apenas durante o treinamento."""
    import keras

    return keras.Sequential(
        [
            keras.layers.RandomFlip("horizontal"),
            keras.layers.RandomRotation(0.08),
            keras.layers.RandomZoom(0.12),
            keras.layers.RandomContrast(0.15),
            keras.layers.RandomBrightness(0.12),
        ],
        name="aumento_de_dados",
    )


def build_datasets(
    processed_dir: Path,
    batch_size: int,
    image_size: int = IMAGE_SIZE,
    seed: int = 42,
):
    """Cria os datasets de treino, validação e teste a partir das pastas.

    Retorna `(treino, validacao, teste)` com `label_mode="categorical"`, ou seja,
    vetores de 2 posições na ordem fixa de `CLASSES` (REGULAR, IRREGULAR).
    """
    import keras

    def _carregar(divisao: str, shuffle: bool):
        return keras.utils.image_dataset_from_directory(
            processed_dir / divisao,
            labels="inferred",
            label_mode="categorical",
            class_names=list(CLASSES),
            color_mode="rgb",
            image_size=(image_size, image_size),
            batch_size=batch_size,
            shuffle=shuffle,
            seed=seed,
        )

    treino = _carregar("train", shuffle=True)
    validacao = _carregar("val", shuffle=False)
    teste = _carregar("test", shuffle=False)
    return treino, validacao, teste


def warm_up(dataset, image_size: int = IMAGE_SIZE):
    """Fixas as dimensões do dataset em memória (evita redecodificar a cada época)."""
    return dataset.cache().prefetch(buffer_size=8)
