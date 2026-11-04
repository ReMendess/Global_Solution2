"""Loop de leitura e envio dos sensores virtuais para o backend.

Uso:

    python -m simulator.sensors.runner                # envia a cada N segundos
    python -m simulator.sensors.runner --once         # uma única rodada
    python -m simulator.sensors.runner --critical     # força transbordamento
    python -m simulator.sensors.runner --interval 5   # intervalo personalizado
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from typing import Any

import requests

from simulator.config import DEFAULT_SENSOR_SPECS, get_settings
from simulator.core.sensor import Sensor

logger = logging.getLogger(__name__)


def build_sensors(specs: list | tuple | None = None) -> list[Sensor]:
    """Cria os sensores a partir das especificações (padrão: seed do backend)."""
    settings = get_settings()
    lista = specs if specs is not None else DEFAULT_SENSOR_SPECS
    return [
        Sensor(
            especificacao,
            step_max=settings.step_max,
            container_depth_cm=settings.container_depth_cm,
        )
        for especificacao in lista
    ]


def send_reading(
    session: requests.Session,
    endpoint: str,
    payload: dict[str, Any],
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Envia uma leitura via HTTP e devolve a resposta JSON do backend.

    Levanta `requests.HTTPError` em caso de status não 2xx.
    """
    resposta = session.post(endpoint, json=payload, timeout=timeout)
    resposta.raise_for_status()
    return resposta.json()


def run_once(
    sensors: list[Sensor],
    session: requests.Session | None = None,
    endpoint: str | None = None,
    timeout: float | None = None,
) -> list[dict[str, Any]]:
    """Avança cada sensor e envia uma leitura, devolvendo os resultados.

    Falhas individuais são registradas no log e não derrubam as demais.
    """
    settings = get_settings()
    sessao = session or requests.Session()
    destino = endpoint or settings.readings_endpoint
    limite = timeout or settings.request_timeout_seconds

    resultados: list[dict[str, Any]] = []
    for sensor in sensors:
        sensor.tick()
        payload = sensor.to_payload()
        try:
            corpo = send_reading(sessao, destino, payload, limite)
            resultados.append(corpo)
            nivel = corpo.get("alert_level", "?")
            logger.info(
                "%s → %s %s%% (alerta %s)",
                payload["sensor_id"],
                payload["container_code"],
                payload["fill_level"],
                nivel,
            )
        except requests.RequestException as exc:
            logger.warning("Falha ao enviar %s: %s", payload["sensor_id"], exc)
    return resultados


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Lê os argumentos de linha de comando."""
    parser = argparse.ArgumentParser(description="Simulador de sensores urbanos (FASE 4).")
    parser.add_argument("--url", type=str, default=None, help="URL do endpoint de telemetria")
    parser.add_argument("--interval", type=float, default=None, help="intervalo entre rodadas (s)")
    parser.add_argument("--once", action="store_true", help="executa uma única rodada")
    parser.add_argument(
        "--critical", action="store_true", help="força os sensores em nível crítico (>= 90%)"
    )
    parser.add_argument(
        "--rounds", type=int, default=None, help="número exato de rodadas (com --interval)"
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI; retorna o código de saída."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    args = parse_args(argv)
    settings = get_settings()

    endpoint = args.url or settings.readings_endpoint
    intervalo = args.interval if args.interval is not None else settings.sensor_interval_seconds

    sensores = build_sensors()
    if args.critical:
        for sensor in sensores:
            sensor.enable_critical()
        logger.info("Modo crítico ativado para %d sensor(es)", len(sensores))

    logger.info("Conectando-se a %s", endpoint)
    with requests.Session() as sessao:
        if args.once:
            run_once(sensores, session=sessao, endpoint=endpoint)
            return 0

        rodadas = 0
        try:
            while args.rounds is None or rodadas < args.rounds:
                inicio = time.perf_counter()
                run_once(sensores, session=sessao, endpoint=endpoint)
                rodadas += 1

                if args.rounds is not None and rodadas >= args.rounds:
                    break

                decorrido = time.perf_counter() - inicio
                time.sleep(max(0.0, intervalo - decorrido))
        except KeyboardInterrupt:
            logger.info("Encerrado pelo usuário após %d rodada(s).", rodadas)

    return 0


if __name__ == "__main__":
    sys.exit(main())
