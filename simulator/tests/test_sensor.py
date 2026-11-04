"""Testes do sensor ultrassônico virtual."""

from __future__ import annotations

import pytest

from simulator.config import SensorSpec
from simulator.core.sensor import Sensor


@pytest.fixture
def sensor() -> Sensor:
    return Sensor(SensorSpec("SENSOR-001", "CONT-001", initial_fill=50.0), seed=42)


@pytest.mark.unit
def test_tick_mantem_ocupacao_dentro_dos_limites(sensor: Sensor) -> None:
    """Após vários ticks, a ocupação nunca sai do intervalo [min, max]."""
    for _ in range(500):
        sensor.tick()

    assert 0.0 <= sensor.fill_level <= 100.0


@pytest.mark.unit
def test_tick_e_deterministico_com_a_mesma_semente() -> None:
    """Mesma semente produz a mesma sequência de ocupação."""
    a = Sensor(SensorSpec("A", "CONT-001", initial_fill=50.0), seed=7)
    b = Sensor(SensorSpec("A", "CONT-001", initial_fill=50.0), seed=7)

    for _ in range(20):
        a.tick()
        b.tick()

    assert a.fill_level == pytest.approx(b.fill_level)


@pytest.mark.unit
def test_force_fill_limitado_ao_intervalo(sensor: Sensor) -> None:
    """force_fill aplica o valor exato e limita valores fora do intervalo."""
    assert sensor.force_fill(72.5) == pytest.approx(72.5)
    assert sensor.force_fill(150.0) == pytest.approx(100.0)
    assert sensor.force_fill(-10.0) == pytest.approx(0.0)


@pytest.mark.unit
def test_distancia_inversamente_proporcional_a_ocupacao(sensor: Sensor) -> None:
    """Contêiner vazio → distância máxima; cheio → distância zero."""
    sensor.force_fill(0.0)
    assert sensor.distance_cm() == pytest.approx(100.0)

    sensor.force_fill(50.0)
    assert sensor.distance_cm() == pytest.approx(50.0)

    sensor.force_fill(100.0)
    assert sensor.distance_cm() == pytest.approx(0.0)


@pytest.mark.unit
def test_modo_critico_mantem_ocupacao_na_faixa_de_transbordamento(sensor: Sensor) -> None:
    """Em modo crítico, a ocupação fica em 90% ou mais."""
    sensor.enable_critical(level=95.0)
    assert sensor.is_critical_mode

    for _ in range(50):
        sensor.tick()

    assert sensor.fill_level >= 90.0


@pytest.mark.unit
def test_to_payload_tem_o_formato_esperado(sensor: Sensor) -> None:
    """O payload segue o contrato do backend (sensor_id, container_code, fill, distance)."""
    sensor.force_fill(80.0)
    payload = sensor.to_payload(measured_at="2026-11-04T10:00:00")

    assert payload["sensor_id"] == "SENSOR-001"
    assert payload["container_code"] == "CONT-001"
    assert payload["fill_level"] == pytest.approx(80.0)
    assert payload["distance_cm"] == pytest.approx(20.0)
    assert payload["measured_at"] == "2026-11-04T10:00:00"


@pytest.mark.unit
def test_to_payload_sem_timestamp_usa_horario_atual(sensor: Sensor) -> None:
    """Sem parâmetro, o payload inclui um timestamp UTC naive em ISO."""
    payload = sensor.to_payload()

    assert isinstance(payload["measured_at"], str)
    assert "T" in payload["measured_at"]
    assert not payload["measured_at"].endswith("Z")
