"""Testes das rotas e do serviço de classificação (FASE 3).

Dois cenários são cobertos:

1. **Sem modelo publicado** — o comportamento esperado é 503, sem quebrar o
   registro de ocorrências.
2. **Com modelo disponível** — usa um modelo Keras minúsculo criado no próprio
   teste (fixture). Ele não é o modelo treinado do projeto: serve apenas para
   exercitar o caminho real de carregamento → pré-processamento → inferência.
"""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path

import pytest
from app.core.config import get_settings
from app.services import classification_service
from fastapi.testclient import TestClient
from PIL import Image

MODEL_INFO = "/api/v1/classification/model-info"
PREDICT = "/api/v1/classification/predict"


def _png_bytes(size=(64, 64), color=(90, 140, 70)) -> bytes:
    """Gera um PNG válido em memória."""
    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return buffer.getvalue()


def _build_tiny_model(path: Path, classes: list[str]) -> None:
    """Cria e salva um modelo Keras mínimo com a mesma interface do modelo real."""
    import keras

    entradas = keras.Input(shape=(224, 224, 3), name="imagem")
    x = keras.layers.Rescaling(1.0 / 127.5, offset=-1.0, name="normalizacao")(entradas)
    x = keras.layers.Conv2D(8, 3, strides=16, activation="relu", name="reducao")(x)
    x = keras.layers.GlobalAveragePooling2D(name="pooling_global")(x)
    saidas = keras.layers.Dense(len(classes), activation="softmax", name="classes")(x)

    modelo = keras.Model(inputs=entradas, outputs=saidas, name="modelo_de_teste")
    modelo.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    modelo.save(path)


@pytest.fixture
def modelo_publicado(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Publica um modelo de fixture + metadados e aponta as configurações para ele."""
    pesos = tmp_path / "modelo_teste.keras"
    metadados = tmp_path / "modelo_teste.metadata.json"

    _build_tiny_model(pesos, ["REGULAR", "IRREGULAR"])
    metadados.write_text(
        json.dumps(
            {
                "model_version": "teste-fixture-v0",
                "classes": ["REGULAR", "IRREGULAR"],
                "image_size": 224,
                "architecture": "modelo mínimo de teste",
                "created_at": "2026-11-04T00:00:00+00:00",
                "metrics": {
                    "accuracy": 0.0,
                    "precision_weighted": 0.0,
                    "recall_weighted": 0.0,
                    "f1_weighted": 0.0,
                    "confusion_matrix": [[0, 0], [0, 0]],
                    "classes": ["REGULAR", "IRREGULAR"],
                },
                "warnings": ["modelo de teste, sem treinamento real"],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    settings = get_settings()
    monkeypatch.setattr(settings, "model_path", pesos)
    monkeypatch.setattr(settings, "model_metadata_path", metadados)
    classification_service.reset_cache()

    yield {"weights": pesos, "metadata": metadados}

    classification_service.reset_cache()


def test_sem_modelo_retorna_503_em_model_info(client: TestClient) -> None:
    """Sem pesos publicados, a rota de metadados responde 503 com orientação."""
    resposta = client.get(MODEL_INFO)

    assert resposta.status_code == 503
    assert "indisponível" in resposta.json()["detail"]


def test_sem_modelo_retorna_503_em_predict(client: TestClient) -> None:
    """Sem pesos publicados, a rota de inferência responde 503."""
    resposta = client.post(PREDICT, files={"image": ("foto.png", _png_bytes(), "image/png")})

    assert resposta.status_code == 503


def test_health_reflete_ausencia_de_modelo(client: TestClient) -> None:
    """O /health continua respondendo, apenas indicando que não há modelo."""
    corpo = client.get("/health").json()

    assert corpo["status"] == "ok"
    assert corpo["model_loaded"] is False


@pytest.mark.integration
def test_model_info_com_modelo_publicado(client: TestClient, modelo_publicado) -> None:
    """Com pesos e metadados, a rota devolve versão, classes e métricas reais."""
    corpo = client.get(MODEL_INFO).json()

    assert corpo["model_version"] == "teste-fixture-v0"
    assert corpo["classes"] == ["REGULAR", "IRREGULAR"]
    assert corpo["image_size"] == 224
    assert corpo["metrics"]["classes"] == ["REGULAR", "IRREGULAR"]
    assert corpo["warnings"]


@pytest.mark.integration
def test_predict_devolve_probabilidades(client: TestClient, modelo_publicado) -> None:
    """A inferência devolve rótulo, confiança e probabilidades coerentes."""
    resposta = client.post(
        PREDICT, files={"image": ("foto.png", _png_bytes((320, 240)), "image/png")}
    )

    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    assert corpo["label"] in {"REGULAR", "IRREGULAR"}
    assert 0.0 <= corpo["confidence"] <= 1.0
    assert set(corpo["probabilities"]) == {"REGULAR", "IRREGULAR"}
    assert abs(sum(corpo["probabilities"].values()) - 1.0) < 0.01
    assert abs(max(corpo["probabilities"].values()) - corpo["confidence"]) < 0.01
    assert corpo["model_version"] == "teste-fixture-v0"


@pytest.mark.integration
def test_predict_rejeita_formato_invalido(client: TestClient, modelo_publicado) -> None:
    """Arquivos que não são JPEG/PNG são recusados com 422."""
    resposta = client.post(PREDICT, files={"image": ("arquivo.txt", b"conteudo", "text/plain")})

    assert resposta.status_code == 422
    assert "não suportado" in resposta.json()["detail"]


@pytest.mark.integration
def test_predict_rejeita_imagem_corrompida(client: TestClient, modelo_publicado) -> None:
    """Bytes inválidos com content-type de imagem resultam em 422."""
    resposta = client.post(PREDICT, files={"image": ("foto.png", b"nao-e-uma-imagem", "image/png")})

    assert resposta.status_code == 422
    assert "ler a imagem" in resposta.json()["detail"]


@pytest.mark.integration
def test_limiar_de_confianca_marca_revisao_humana(
    client: TestClient, modelo_publicado, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Confiança abaixo do limiar configurado exige revisão humana."""
    settings = get_settings()

    monkeypatch.setattr(settings, "confidence_threshold", 1.0)
    exigindo = client.post(PREDICT, files={"image": ("a.png", _png_bytes(), "image/png")}).json()

    monkeypatch.setattr(settings, "confidence_threshold", 0.0)
    sem_exigir = client.post(PREDICT, files={"image": ("b.png", _png_bytes(), "image/png")}).json()

    assert exigindo["needs_human_review"] is True
    assert sem_exigir["needs_human_review"] is False


@pytest.mark.integration
def test_ocorrencia_usa_classificacao_do_modelo(client: TestClient, modelo_publicado) -> None:
    """O registro de ocorrência passa a gravar rótulo, confiança e versão do modelo."""
    resposta = client.post(
        "/api/v1/occurrences",
        data={"neighborhood": "Pinheiros", "description": "Teste de integração da FASE 3"},
        files={"image": ("foto.png", _png_bytes(), "image/png")},
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["model_label"] in {"REGULAR", "IRREGULAR"}
    assert corpo["confidence"] is not None
    assert corpo["model_version"] == "teste-fixture-v0"


def test_metadados_ilegiveis_nao_derrubam_a_api(
    client: TestClient, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """JSON inválido nos metadados faz a API cair para os valores padrão."""
    pesos = tmp_path / "modelo.keras"
    _build_tiny_model(pesos, ["REGULAR", "IRREGULAR"])
    metadados = tmp_path / "invalido.json"
    metadados.write_text("{ isso nao e json", encoding="utf-8")

    settings = get_settings()
    monkeypatch.setattr(settings, "model_path", pesos)
    monkeypatch.setattr(settings, "model_metadata_path", metadados)
    classification_service.reset_cache()

    corpo = client.get(MODEL_INFO).json()

    assert corpo["model_version"] == "unavailable"
    assert corpo["classes"] == ["REGULAR", "IRREGULAR"]
    classification_service.reset_cache()


@pytest.mark.unit
def test_build_result_seleciona_maior_probabilidade() -> None:
    """O rótulo vem do índice de maior probabilidade, com revisão humana coerente."""
    resultado = classification_service._build_result([0.2, 0.8], ["REGULAR", "IRREGULAR"], "v1")

    assert resultado.label == "IRREGULAR"
    assert resultado.confidence == 0.8
    assert resultado.probabilities == {"REGULAR": 0.2, "IRREGULAR": 0.8}
