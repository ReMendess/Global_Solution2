"""Testes do portal administrativo fictício."""

from __future__ import annotations

import re
import threading

import pytest
import requests

from rpa.portal.server import PortalServer

_PREFIXO = re.compile(r'id="portal-protocol">\s*([A-Za-z0-9-]+)\s*<')


@pytest.fixture(scope="module")
def portal():
    """Sobe o portal em uma porta efêmera e encerra ao final do módulo."""
    servidor = PortalServer(("127.0.0.1", 0))
    thread = threading.Thread(target=servidor.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{servidor.server_address[1]}"
    yield {"server": servidor, "base": base}
    servidor.shutdown()
    servidor.server_close()


def test_get_formulario(portal) -> None:
    """A raiz serve o formulário do portal."""
    resposta = requests.get(f"{portal['base']}/", timeout=5)

    assert resposta.status_code == 200
    assert "Portal Administrativo" in resposta.text
    assert 'id="submit-button"' in resposta.text


def test_submissao_retorna_protocolo(portal) -> None:
    """O POST devolve uma confirmação com o protocolo do portal."""
    resposta = requests.post(
        f"{portal['base']}/submit",
        data={"protocol": "CL-2026-000001", "category": "OVERFLOW"},
        timeout=5,
    )

    assert resposta.status_code == 200
    assert "portal-protocol" in resposta.text
    assert "PORTAL-" in resposta.text


def test_protocolos_sao_sequenciais_e_registrados(portal) -> None:
    """Cada submissão gera um protocolo novo e fica no histórico."""
    primeira = requests.post(f"{portal['base']}/submit", data={"protocol": "CL-1"}, timeout=5)
    segunda = requests.post(f"{portal['base']}/submit", data={"protocol": "CL-2"}, timeout=5)

    protocolo_1 = _PREFIXO.search(primeira.text)
    protocolo_2 = _PREFIXO.search(segunda.text)

    assert protocolo_1 and protocolo_2
    assert protocolo_1.group(1) != protocolo_2.group(1)
    assert len(portal["server"].historico) >= 2


def test_recurso_inexistente_retorna_404(portal) -> None:
    """Caminho desconhecido responde 404."""
    resposta = requests.get(f"{portal['base']}/nao-existe", timeout=5)

    assert resposta.status_code == 404
