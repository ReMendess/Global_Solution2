"""Testes do loop de envio do simulador."""

from __future__ import annotations

from typing import Any

import pytest
import requests

from simulator.config import DEFAULT_SENSOR_SPECS, SensorSpec
from simulator.core.sensor import Sensor
from simulator.sensors.runner import build_sensors, run_once, send_reading


class FakeResponse:
    """Resposta HTTP falsa para os testes do runner."""

    def __init__(self, body: dict[str, Any], status: int = 201) -> None:
        self._body = body
        self.status_code = status

    def json(self) -> dict[str, Any]:
        return self._body

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    """Sessão falsa que registra as requisições enviadas."""

    def __init__(self, *, falha: bool = False) -> None:
        self.posts: list[tuple[str, dict[str, Any], float]] = []
        self.falha = falha

    def post(self, endpoint: str, json: dict[str, Any], timeout: float) -> FakeResponse:
        self.posts.append((endpoint, json, timeout))
        if self.falha:
            return FakeResponse({"detail": "erro"}, status=503)
        return FakeResponse({"alert_level": "HIGH", "id": len(self.posts)})


def _specs(n: int = 3) -> list[SensorSpec]:
    return [SensorSpec(f"SENSOR-00{i}", f"CONT-00{i}", initial_fill=50.0) for i in range(1, n + 1)]


@pytest.mark.unit
def test_build_sensors_cria_um_sensor_por_especificacao() -> None:
    """Sem argumentos, usa as especificações padrão (6 sensores do seed)."""
    sensores = build_sensors()

    assert len(sensores) == len(DEFAULT_SENSOR_SPECS)
    assert all(isinstance(s, Sensor) for s in sensores)
    assert [s.spec.sensor_id for s in sensores] == [
        especificacao.sensor_id for especificacao in DEFAULT_SENSOR_SPECS
    ]


@pytest.mark.unit
def test_send_reading_envia_payload_e_devolve_json() -> None:
    """O envio usa POST com JSON e retorna o corpo da resposta."""
    sessao = FakeSession()

    corpo = send_reading(sessao, "http://x/api", {"a": 1}, timeout=3.0)

    assert corpo == {"alert_level": "HIGH", "id": 1}
    endpoint, payload, timeout = sessao.posts[0]
    assert endpoint == "http://x/api"
    assert payload == {"a": 1}
    assert timeout == 3.0


@pytest.mark.unit
def test_run_once_avanca_e_envia_todos_os_sensores() -> None:
    """Cada sensor tem tick + envio; falha individual não derruba o resto."""
    sessao = FakeSession()
    sensores = build_sensors(_specs(3))

    resultados = run_once(sensores, session=sessao, endpoint="http://x/api")

    assert len(resultados) == 3
    assert len(sessao.posts) == 3
    enviados = [payload["sensor_id"] for _, payload, _ in sessao.posts]
    assert enviados == ["SENSOR-001", "SENSOR-002", "SENSOR-003"]


@pytest.mark.unit
def test_run_once_continua_apos_falha_individual() -> None:
    """Quando o envio falha, a rodada não é abortada e os demais são processados."""
    sessao = FakeSession(falha=True)
    sensores = build_sensors(_specs(2))

    resultados = run_once(sensores, session=sessao, endpoint="http://x/api")

    assert resultados == []
    assert len(sessao.posts) == 2  # ainda tenta enviar todos
