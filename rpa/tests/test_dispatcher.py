"""Testes do robô de despacho (funções puras e interação com página fake)."""

from __future__ import annotations

from rpa.bot.dispatcher import build_form_data, dispatch_one, parse_portal_protocol
from rpa.bot.selectors import SELECTORS


def test_build_form_data_preenche_campos() -> None:
    """Os campos do formulário são extraídos do item da fila."""
    ocorrencia = {
        "protocol": "CL-1",
        "category": "OVERFLOW",
        "priority": "HIGH",
        "neighborhood": "Pinheiros",
        "address": "",
        "description": "teste",
    }

    dados = build_form_data(ocorrencia)

    assert dados["protocol"] == "CL-1"
    assert dados["category"] == "OVERFLOW"
    assert dados["address"] == ""
    assert dados["description"] == "teste"


def test_parse_portal_protocol() -> None:
    """O protocolo é extraído do `<span id=\"portal-protocol\">`."""
    html = '<div>ok</div><span id="portal-protocol">PORTAL-0001</span>'

    assert parse_portal_protocol(html) == "PORTAL-0001"
    assert parse_portal_protocol("sem protocolo aqui") is None


class FakePage:
    """Substituto da `Page` do Playwright para os testes."""

    def __init__(self, content_after_submit: str) -> None:
        self.goto_url: str | None = None
        self.filled: dict[str, str] = {}
        self.clicked: list[str] = []
        self._content = content_after_submit

    def goto(self, url: str) -> None:
        self.goto_url = url

    def fill(self, selector: str, value: str) -> None:
        self.filled[selector] = value

    def click(self, selector: str) -> None:
        self.clicked.append(selector)

    def wait_for_selector(self, selector: str) -> None:
        return None

    def content(self) -> str:
        return self._content


def test_dispatch_one_preenche_e_captura_protocolo() -> None:
    """O robô preenche todos os campos e captura o protocolo."""
    page = FakePage('<span id="portal-protocol">PORTAL-0042</span>')
    ocorrencia = {
        "protocol": "CL-2026-000001",
        "category": "OVERFLOW",
        "priority": "CRITICAL",
        "neighborhood": "Butantã",
        "address": "Rua A, 1",
        "description": "transbordando",
    }

    resultado = dispatch_one(page, ocorrencia, "http://portal")

    assert page.goto_url == "http://portal"
    assert page.filled[SELECTORS["protocol"]] == "CL-2026-000001"
    assert page.filled[SELECTORS["priority"]] == "CRITICAL"
    assert SELECTORS["submit"] in page.clicked
    assert resultado == "PORTAL-0042"


def test_dispatch_one_ignora_campos_vazios() -> None:
    """Campos ausentes/vazios não são preenchidos no formulário."""
    page = FakePage('<span id="portal-protocol">PORTAL-0009</span>')
    ocorrencia = {
        "protocol": "CL-2",
        "category": "OTHER",
        "priority": "LOW",
        "neighborhood": "Santana",
        "address": None,
        "description": "",
    }

    dispatch_one(page, ocorrencia, "http://portal")

    assert SELECTORS["address"] not in page.filled
    assert SELECTORS["description"] not in page.filled
    assert page.filled[SELECTORS["neighborhood"]] == "Santana"
