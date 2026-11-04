"""Testes de integração das rotas de ocorrências."""

from __future__ import annotations

from io import BytesIO

import pytest
from app.core.config import get_settings
from fastapi.testclient import TestClient
from PIL import Image

ENDPOINT = "/api/v1/occurrences"


def _png() -> bytes:
    """Gera um PNG válido pequeno para o upload."""
    buffer = BytesIO()
    Image.new("RGB", (16, 16), (140, 170, 110)).save(buffer, format="PNG")
    return buffer.getvalue()


def _criar(client: TestClient, **campos: str) -> dict:
    """Cria uma ocorrência sem imagem e devolve o corpo da resposta."""
    dados = {"neighborhood": "Pinheiros", "description": "Registro de teste"}
    dados.update(campos)
    resposta = client.post(ENDPOINT, data=dados)
    assert resposta.status_code == 201, resposta.text
    return resposta.json()


@pytest.mark.integration
def test_criar_ocorrencia_gera_protocolo_e_historico(client: TestClient) -> None:
    """O registro deve persistir, gerar protocolo e abrir a trilha de status."""
    corpo = _criar(client, reported_category="OVERFLOW")

    assert corpo["protocol"].startswith("CL-")
    assert corpo["protocol"].endswith("000001")
    assert corpo["is_simulated"] is False
    assert corpo["status"] in {"OPEN", "CLASSIFIED", "PENDING_DISPATCH"}
    assert corpo["needs_human_review"] is True
    assert corpo["priority"] == "HIGH"
    assert [item["to_status"] for item in corpo["status_history"]] == ["OPEN"]


@pytest.mark.integration
def test_consulta_por_protocolo_devolve_ocorrencia_persistida(client: TestClient) -> None:
    """O cidadão consulta o status usando o protocolo recebido."""
    criada = _criar(client, neighborhood="Butantã")

    resposta = client.get(f"{ENDPOINT}/protocol/{criada['protocol']}")

    assert resposta.status_code == 200
    assert resposta.json()["id"] == criada["id"]
    assert resposta.json()["neighborhood"] == "Butantã"


@pytest.mark.integration
def test_protocolo_inexistente_retorna_404(client: TestClient) -> None:
    """Protocolo desconhecido deve retornar 404 com mensagem clara."""
    resposta = client.get(f"{ENDPOINT}/protocol/CL-2026-999999")

    assert resposta.status_code == 404
    assert "não encontrado" in resposta.json()["detail"]


@pytest.mark.integration
def test_protocolos_sao_sequenciais(client: TestClient) -> None:
    """Cada nova ocorrência recebe o próximo número da sequência."""
    primeira = _criar(client, neighborhood="Butantã", description="Primeira")
    segunda = _criar(client, neighborhood="Tatuapé", description="Segunda")

    assert primeira["protocol"].endswith("000001")
    assert segunda["protocol"].endswith("000002")


@pytest.mark.integration
def test_ocorrencia_duplicada_retorna_409_com_protocolo_original(
    client: TestClient,
) -> None:
    """Registrar o mesmo local no mesmo dia deve ser bloqueado."""
    original = _criar(client, latitude="-23.5678", longitude="-46.6920")

    resposta = client.post(
        ENDPOINT,
        data={
            "neighborhood": "Pinheiros",
            "latitude": "-23.5678",
            "longitude": "-46.6920",
            "description": "Tentativa duplicada",
        },
    )

    assert resposta.status_code == 409
    assert original["protocol"] in resposta.json()["detail"]


@pytest.mark.integration
def test_upload_de_imagem_persiste_arquivo_e_marca_revisao(client: TestClient) -> None:
    """A imagem é gravada em disco e a ocorrência passa por CLASSIFIED."""
    resposta = client.post(
        ENDPOINT,
        data={"neighborhood": "Vila Madalena", "reported_category": "ILLEGAL_DUMPING"},
        files={"image": ("foto.png", _png(), "image/png")},
    )

    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert len(corpo["images"]) == 1
    imagem = corpo["images"][0]
    assert imagem["content_type"] == "image/png"
    assert imagem["file_path"].endswith(".png")
    assert imagem["width"] == 16
    assert imagem["height"] == 16
    assert [item["to_status"] for item in corpo["status_history"]] == ["OPEN", "CLASSIFIED"]

    arquivo = get_settings().resolved_upload_dir / imagem["file_path"]
    assert arquivo.is_file()
    assert arquivo.stat().st_size == imagem["size_bytes"]


@pytest.mark.integration
def test_formato_de_imagem_invalido_retorna_422(client: TestClient) -> None:
    """Arquivos que não são JPEG/PNG são recusados."""
    resposta = client.post(
        ENDPOINT,
        data={"neighborhood": "Itaim Bibi"},
        files={"image": ("nota.txt", b"conteudo", "text/plain")},
    )

    assert resposta.status_code == 422
    assert "não suportado" in resposta.json()["detail"]


@pytest.mark.integration
def test_imagem_acima_do_limite_retorna_413(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Imagens acima de MAX_UPLOAD_MB são recusadas com 413."""
    monkeypatch.setattr(get_settings(), "max_upload_mb", 0)

    resposta = client.post(
        ENDPOINT,
        data={"neighborhood": "Santana"},
        files={"image": ("foto.png", _png(), "image/png")},
    )

    assert resposta.status_code == 413
