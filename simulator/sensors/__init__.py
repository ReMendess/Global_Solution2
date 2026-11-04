"""Loops de envio das leituras dos sensores virtuais.

Use `from simulator.sensors.runner import build_sensors, run_once` para importar
diretamente. A importação é feita sob demanda para permitir
`python -m simulator.sensors.runner` sem avisos de importação circular.
"""

__all__ = ["build_sensors", "run_once", "send_reading"]
