"""Núcleo do simulador: sensor ultrassônico virtual.

Use `from simulator.core.sensor import Sensor` para importar diretamente.
A importação é feita sob demanda para permitir `python -m simulator.sensors.runner`
sem avisos de importação circular.
"""

__all__ = ["Sensor"]
