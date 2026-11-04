"""Sensor ultrassônico virtual que representa um contêiner urbano.

Cada sensor tem um identificador único, está associado a um contêiner e gera
variações de ocupação por um passeio aleatório limitado (random walk). A distância
medida pelo ultrassônico é inversamente proporcional à ocupação: contêiner vazio →
distância máxima (profundidade); contêiner cheio → distância zero.
"""

from __future__ import annotations

import random
from datetime import UTC, datetime
from typing import Any

from simulator.config import SensorSpec


def now_utc_naive_iso() -> str:
    """Data/hora atual em UTC sem timezone (convenção adotada no projeto)."""
    return datetime.now(UTC).replace(tzinfo=None).isoformat()


class Sensor:
    """Sensor virtual com estado de ocupação e capacidade de medição."""

    def __init__(
        self,
        spec: SensorSpec,
        *,
        step_max: float = 3.0,
        container_depth_cm: float = 100.0,
        seed: int | None = None,
    ) -> None:
        self.spec = spec
        self.step_max = step_max
        self.container_depth_cm = container_depth_cm
        self._rng = random.Random(seed)
        self.fill_level = self._clamp(spec.initial_fill)
        self._critical = False

    # ------------------------------------------------------------------
    # Estado e evolução da ocupação
    # ------------------------------------------------------------------
    def _clamp(self, valor: float) -> float:
        return max(self.spec.min_fill, min(self.spec.max_fill, valor))

    def tick(self) -> float:
        """Avança uma leitura: varia a ocupação dentro dos limites.

        Em modo crítico, mantém a ocupação na faixa de transbordamento (>= 90%).
        """
        if self._critical:
            self.fill_level = self._rng.uniform(90.0, self.spec.max_fill)
        else:
            delta = self._rng.uniform(-self.step_max, self.step_max)
            self.fill_level = self._clamp(self.fill_level + delta)
        return self.fill_level

    def force_fill(self, valor: float) -> float:
        """Define a ocupação para um valor exato (limitado ao intervalo)."""
        self.fill_level = self._clamp(valor)
        return self.fill_level

    def enable_critical(self, level: float = 95.0) -> None:
        """Coloca o sensor em modo de simulação de transbordamento."""
        self._critical = True
        self.fill_level = self._clamp(level)

    @property
    def is_critical_mode(self) -> bool:
        return self._critical

    # ------------------------------------------------------------------
    # Medição
    # ------------------------------------------------------------------
    def distance_cm(self) -> float:
        """Distância do ultrassônico ao topo do material (0 = cheio)."""
        amplitude = self.spec.max_fill - self.spec.min_fill
        if amplitude <= 0:
            return 0.0
        fracao_vazia = (self.spec.max_fill - self.fill_level) / amplitude
        return round(max(0.0, fracao_vazia) * self.container_depth_cm, 1)

    # ------------------------------------------------------------------
    # Saída
    # ------------------------------------------------------------------
    def to_payload(self, measured_at: str | None = None) -> dict[str, Any]:
        """Monta o payload HTTP no formato aceito pelo backend."""
        return {
            "sensor_id": self.spec.sensor_id,
            "container_code": self.spec.container_code,
            "fill_level": round(self.fill_level, 2),
            "distance_cm": self.distance_cm(),
            "measured_at": measured_at or now_utc_naive_iso(),
        }
