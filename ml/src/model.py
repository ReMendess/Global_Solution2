"""Construção do modelo MobileNetV2 com transfer learning.

O modelo salvo é autocontido: a normalização para [-1, 1] é uma camada interna,
então o backend pode enviar pixels crus em [0, 255] sem repetir a lógica.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ml.src.config import (
    CLASSES,
    DROPOUT,
    IMAGE_SIZE,
    LEARNING_RATE_HEAD,
    RESCALE_OFFSET,
    RESCALE_SCALE,
    UNFREEZE_LAYERS,
)

if TYPE_CHECKING:  # pragma: no cover - apenas tipagem
    import keras

BASE_LAYER_NAME = "mobilenetv2_1.00_224"


def build_model(
    image_size: int = IMAGE_SIZE,
    learning_rate: float = LEARNING_RATE_HEAD,
    dropout: float = DROPOUT,
) -> keras.Model:
    """Cria o classificador com a base MobileNetV2 congelada.

    A saída tem 2 neurônios (softmax) na ordem fixa de `CLASSES`,
    exatamente como o backend consome na inferência.
    """
    import keras

    base = keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False  # etapa 1: apenas a cabeça é treinada

    entradas = keras.Input(shape=(image_size, image_size, 3), name="imagem")
    x = keras.layers.Rescaling(RESCALE_SCALE, offset=RESCALE_OFFSET, name="normalizacao")(entradas)
    x = base(x, training=False)
    x = keras.layers.GlobalAveragePooling2D(name="pooling_global")(x)
    x = keras.layers.Dropout(dropout, name="dropout")(x)
    saidas = keras.layers.Dense(len(CLASSES), activation="softmax", name="classes")(x)

    modelo = keras.Model(inputs=entradas, outputs=saidas, name="cidade_limpa_mobilenetv2")
    modelo.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return modelo


def unfreeze_top_layers(
    model: keras.Model,
    num_layers: int = UNFREEZE_LAYERS,
    learning_rate: float = 1e-5,
) -> int:
    """Libera as últimas `num_layers` camadas da base para o ajuste fino.

    Camadas de BatchNormalization continuam congeladas: com lotes pequenos elas
    degradam as estatísticas aprendidas no ImageNet.
    """
    import keras

    base = model.get_layer(BASE_LAYER_NAME)
    base.trainable = True

    liberadas = 0
    for camada in base.layers[:-num_layers] if num_layers > 0 else []:
        camada.trainable = False

    for camada in base.layers[-num_layers:] if num_layers > 0 else []:
        if isinstance(camada, keras.layers.BatchNormalization):
            camada.trainable = False
        else:
            camada.trainable = True
            liberadas += 1

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return liberadas


def count_trainable_params(model: keras.Model) -> tuple[int, int]:
    """Retorna (parâmetros treináveis, parâmetros totais)."""
    treinaveis = int(
        sum(int(w.shape.num_elements() or 0) for w in model.trainable_weights if w.shape.rank)
    )
    total = int(model.count_params())
    return treinaveis, total
