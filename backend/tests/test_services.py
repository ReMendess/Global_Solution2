"""Testes unitários das regras puras (prioridade, alerta e deduplicação)."""

from __future__ import annotations

from datetime import datetime

import pytest
from app.core.config import get_settings
from app.core.enums import AlertLevel, OccurrenceCategory, Priority
from app.services.container_service import resolve_alert_level
from app.services.dedup_service import build_dedup_hash
from app.services.priority_service import raise_priority, resolve_priority


@pytest.mark.unit
@pytest.mark.parametrize(
    ("nivel", "esperado"),
    [
        (0.0, AlertLevel.NORMAL),
        (79.9, AlertLevel.NORMAL),
        (80.0, AlertLevel.HIGH),
        (89.9, AlertLevel.HIGH),
        (90.0, AlertLevel.CRITICAL),
        (100.0, AlertLevel.CRITICAL),
    ],
)
def test_limiares_de_alerta(nivel: float, esperado: AlertLevel) -> None:
    """Os limites 80% e 90% seguem exatamente o PROJECT_CONTEXT.md §6."""
    assert resolve_alert_level(nivel) == esperado


@pytest.mark.unit
def test_prioridade_sobe_um_nivel_por_categoria() -> None:
    """OVERFLOW e DAMAGED_CONTAINER elevam a prioridade calculada."""
    base, _ = resolve_priority(
        category=OccurrenceCategory.ILLEGAL_DUMPING,
        model_label=None,
        confidence=None,
    )
    overflow, _ = resolve_priority(
        category=OccurrenceCategory.OVERFLOW,
        model_label=None,
        confidence=None,
    )

    assert base == Priority.MEDIUM
    assert overflow == Priority.HIGH


@pytest.mark.unit
def test_prioridade_nunca_ultrapassa_critica() -> None:
    """O incremento de prioridade é limitado a CRITICAL."""
    assert raise_priority(Priority.CRITICAL, 3) == Priority.CRITICAL
    assert raise_priority(Priority.LOW, 2) == Priority.HIGH


@pytest.mark.unit
def test_modelo_indisponivel_exige_revisao_humana() -> None:
    """Sem modelo, a prioridade é MEDIUM e a revisão humana é obrigatória."""
    prioridade, revisao = resolve_priority(
        category=OccurrenceCategory.ILLEGAL_DUMPING,
        model_label=None,
        confidence=None,
    )

    assert prioridade == Priority.MEDIUM
    assert revisao is True


@pytest.mark.unit
def test_classificacao_irregular_confiavel_nao_exige_revisao() -> None:
    """IRREGULAR com confiança alta resulta em prioridade HIGH sem revisão."""
    prioridade, revisao = resolve_priority(
        category=OccurrenceCategory.ILLEGAL_DUMPING,
        model_label="IRREGULAR",
        confidence=0.93,
    )

    assert prioridade == Priority.HIGH
    assert revisao is False


@pytest.mark.unit
def test_classificacao_abaixo_do_limiar_exige_revisao() -> None:
    """Confiança menor que o limiar configurado marca revisão humana."""
    limiar = get_settings().confidence_threshold
    prioridade, revisao = resolve_priority(
        category=OccurrenceCategory.ILLEGAL_DUMPING,
        model_label="IRREGULAR",
        confidence=limiar - 0.05,
    )

    assert prioridade == Priority.MEDIUM
    assert revisao is True


@pytest.mark.unit
def test_categoria_other_sempre_exige_revisao() -> None:
    """Categoria OTHER não é encaminhável automaticamente."""
    _, revisao = resolve_priority(
        category=OccurrenceCategory.OTHER,
        model_label="REGULAR",
        confidence=0.99,
    )

    assert revisao is True


@pytest.mark.unit
def test_hash_de_deduplicacao_estavel_e_sensivel() -> None:
    """O hash é determinístico e muda quando o bairro muda."""
    referencia = datetime(2026, 11, 4, 10, 0, 0)
    base = build_dedup_hash(
        neighborhood="Pinheiros",
        category="OVERFLOW",
        latitude=-23.56781,
        longitude=-46.69201,
        reference=referencia,
    )
    mesmo_local = build_dedup_hash(
        neighborhood=" pinheiros ",
        category="OVERFLOW",
        latitude=-23.56782,
        longitude=-46.69203,
        reference=referencia,
    )
    outro_bairro = build_dedup_hash(
        neighborhood="Butantã",
        category="OVERFLOW",
        latitude=-23.56781,
        longitude=-46.69201,
        reference=referencia,
    )

    assert base == mesmo_local
    assert base != outro_bairro
    assert len(base) == 64


@pytest.mark.unit
def test_hash_e_none_sem_coordenadas() -> None:
    """Sem coordenadas não há deduplicação (retorna None)."""
    referencia = datetime(2026, 11, 4, 10, 0, 0)

    assert (
        build_dedup_hash(
            neighborhood="Pinheiros",
            category="OVERFLOW",
            latitude=None,
            longitude=None,
            reference=referencia,
        )
        is None
    )
    assert (
        build_dedup_hash(
            neighborhood="Pinheiros",
            category="OVERFLOW",
            latitude=-23.5678,
            longitude=None,
            reference=referencia,
        )
        is None
    )
    assert (
        build_dedup_hash(
            neighborhood="Pinheiros",
            category="OVERFLOW",
            latitude=None,
            longitude=-46.692,
            reference=referencia,
        )
        is None
    )
