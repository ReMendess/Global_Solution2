"""Simulador de IoT do Cidade Limpa (FASE 4).

Sensores ultrassônicos virtuais que representam contêineres urbanos e enviam
telemetria (ocupação + distância) via HTTP para o backend FastAPI.

Execução:

    python -m simulator.sensors.runner --help
"""

__all__ = ["config", "core", "sensors"]
