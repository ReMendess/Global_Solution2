"""Testes da entrega estática de imagens enviadas (usada pelo frontend)."""

from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def _png() -> bytes:
    """Gera um PNG válido pequeno."""
    buffer = BytesIO()
    Image.new("RGB", (12, 12), (30, 90, 60)).save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.integration
def test_imagem_enviada_pode_ser_baixada_por_url(client: TestClient) -> None:
    """A imagem gravada em data/uploads é servida em /uploads/{arquivo}."""
    criada = client.post(
        "/api/v1/occurrences",
        data={"neighborhood": "Pinheiros", "description": "Teste de entrega estática"},
        files={"image": ("foto.png", _png(), "image/png")},
    ).json()

    arquivo = criada["images"][0]["file_path"]
    resposta = client.get(f"/uploads/{arquivo}")

    assert resposta.status_code == 200
    assert resposta.headers["content-type"] == "image/png"
    assert len(resposta.content) == criada["images"][0]["size_bytes"]


@pytest.mark.integration
def test_arquivo_inexistente_retorna_404(client: TestClient) -> None:
    """Arquivo inexistente em /uploads responde 404."""
    assert client.get("/uploads/nao-existe.png").status_code == 404
