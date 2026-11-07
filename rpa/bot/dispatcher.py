"""Robô de despacho (RPA).

Consulta a fila da API, abre o portal administrativo fictício, preenche os dados,
submete, captura o protocolo e devolve o resultado à API.

Execução:

    python -m rpa.bot.dispatcher
    python -m rpa.bot.dispatcher --max-demands 3
"""

from __future__ import annotations

import argparse
import logging
import re
import time
from typing import Any

import requests

from rpa.bot.selectors import FORM_FIELDS, SELECTORS
from rpa.config import get_settings

logger = logging.getLogger(__name__)

_PROTOCOL_PATTERN = re.compile(r'id="portal-protocol">\s*([A-Za-z0-9-]+)\s*<')


# ----------------------------------------------------------------------
# Funções puras (testáveis sem navegador/rede)
# ----------------------------------------------------------------------
def build_form_data(occurrence: dict[str, Any]) -> dict[str, str]:
    """Mapeia um item da fila para os campos do formulário do portal."""
    return {campo: str(occurrence.get(campo) or "") for campo in FORM_FIELDS}


def parse_portal_protocol(html_text: str) -> str | None:
    """Extrai o protocolo gerado pelo portal a partir da página de confirmação."""
    match = _PROTOCOL_PATTERN.search(html_text)
    return match.group(1) if match else None


# ----------------------------------------------------------------------
# Acesso à API do backend
# ----------------------------------------------------------------------
def fetch_queue(api_base_url: str, timeout: float = 10.0) -> list[dict[str, Any]]:
    """Consulta a fila de demandas elegíveis."""
    url = f"{api_base_url.rstrip('/')}/api/v1/rpa/queue"
    resposta = requests.get(url, timeout=timeout)
    resposta.raise_for_status()
    return list(resposta.json()["items"])


def report_execution(
    api_base_url: str,
    occurrence_id: int,
    status: str,
    *,
    portal_protocol: str | None = None,
    error_message: str | None = None,
    duration_ms: int | None = None,
    screenshot_path: str | None = None,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """Registra o resultado de uma execução na API."""
    url = f"{api_base_url.rstrip('/')}/api/v1/rpa/executions"
    payload: dict[str, Any] = {
        "occurrence_id": occurrence_id,
        "status": status,
        "portal_protocol": portal_protocol,
        "duration_ms": duration_ms,
        "error_message": error_message,
        "screenshot_path": screenshot_path,
    }
    resposta = requests.post(url, json=payload, timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()


# ----------------------------------------------------------------------
# Interação com o portal via Playwright
# ----------------------------------------------------------------------
def dispatch_one(
    page: Any,
    occurrence: dict[str, Any],
    portal_url: str,
    selectors: dict[str, str] | None = None,
) -> str | None:
    """Preenche e submete o formulário, devolvendo o protocolo capturado.

    `page` é uma `Page` do Playwright; em testes, um substituto com a mesma
    interface (`goto`, `fill`, `click`, `wait_for_selector`, `content`).
    """
    seletores = selectors or SELECTORS
    dados = build_form_data(occurrence)
    page.goto(portal_url)

    for campo in FORM_FIELDS:
        seletor = seletores.get(campo)
        valor = dados.get(campo)
        if seletor and valor:
            page.fill(seletor, valor)

    page.click(seletores["submit"])
    page.wait_for_selector(seletores["protocol_result"])
    return parse_portal_protocol(page.content())


# ----------------------------------------------------------------------
# Orquestração
# ----------------------------------------------------------------------
def run_bot(
    *,
    api_base_url: str | None = None,
    portal_url: str | None = None,
    headless: bool | None = None,
    max_demands: int | None = None,
) -> int:
    """Processa a fila de demandas e devolve o número de itens processados."""
    settings = get_settings()
    api = api_base_url or settings.api_base_url
    portal = portal_url or settings.rpa_portal_url
    navegador_headless = settings.rpa_headless if headless is None else headless
    limite = max_demands if max_demands is not None else settings.max_demands

    fila = fetch_queue(api, settings.request_timeout_seconds)
    if not fila:
        logger.info("Fila vazia: nada a processar.")
        return 0

    demandas = fila[:limite] if limite else fila
    logger.info("Processando %d demanda(s) de %d na fila", len(demandas), len(fila))

    from playwright.sync_api import sync_playwright

    processadas = 0
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(headless=navegador_headless)
        pagina = navegador.new_page()

        for ocorrencia in demandas:
            occurrencia_id = int(ocorrencia["occurrence_id"])
            inicio = time.perf_counter()
            try:
                protocolo_portal = dispatch_one(pagina, ocorrencia, portal)
                duracao = int((time.perf_counter() - inicio) * 1000)
                if not protocolo_portal:
                    raise RuntimeError("Portal não devolveu o protocolo.")
                report_execution(
                    api,
                    occurrencia_id,
                    "SUCCESS",
                    portal_protocol=protocolo_portal,
                    duration_ms=duracao,
                )
                logger.info(
                    "OK %s -> %s (%d ms)",
                    ocorrencia.get("protocol"),
                    protocolo_portal,
                    duracao,
                )
            except Exception as exc:  # noqa: BLE001 - registra qualquer falha sem abortar
                duracao = int((time.perf_counter() - inicio) * 1000)
                report_execution(
                    api,
                    occurrencia_id,
                    "FAILED",
                    error_message=str(exc)[:2000],
                    duration_ms=duracao,
                )
                logger.warning("FALHA %s: %s", ocorrencia.get("protocol"), exc)
            processadas += 1

        navegador.close()
    return processadas


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    parser = argparse.ArgumentParser(description="Robô de despacho do Smart Clean City (FASE 5).")
    parser.add_argument("--api-base-url", default=None)
    parser.add_argument("--portal-url", default=None)
    parser.add_argument("--max-demands", type=int, default=None)
    parser.add_argument("--headless", action="store_true", default=None)
    args = parser.parse_args(argv)

    processadas = run_bot(
        api_base_url=args.api_base_url,
        portal_url=args.portal_url,
        headless=args.headless or None,
        max_demands=args.max_demands,
    )
    logger.info("Concluído: %d demanda(s) processada(s).", processadas)
    return 0


if __name__ == "__main__":
    main()
