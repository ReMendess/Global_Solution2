"""Ferramentas do agente: consultam serviços reais e nunca inventam dados."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.core.enums import OccurrenceCategory
from app.core.exceptions import ConflictError, NotFoundError
from app.schemas.occurrence import OccurrenceCreate
from app.services import container_service, dashboard_service, occurrence_service


@dataclass(slots=True)
class ToolResult:
    """Resultado de uma ferramenta (dados + resposta em linguagem natural)."""

    data: dict[str, Any] | None
    response: str


# ----------------------------------------------------------------------
# consultar_ocorrencia
# ----------------------------------------------------------------------
def consultar_ocorrencia(db: Session, protocol: str) -> ToolResult:
    """Consulta uma ocorrência pelo protocolo."""
    try:
        ocorrencia = occurrence_service.get_by_protocol(db, protocol)
    except NotFoundError:
        return ToolResult(
            data=None,
            response=f"Não encontrei nenhuma ocorrência com o protocolo {protocol}.",
        )

    dados = ocorrencia.model_dump(mode="json")
    return ToolResult(
        data=dados,
        response=(
            f"A ocorrência {ocorrencia.protocol} está com status {ocorrencia.status.value}, "
            f"categoria {ocorrencia.category.value} e prioridade {ocorrencia.priority.value}."
        ),
    )


# ----------------------------------------------------------------------
# consultar_container
# ----------------------------------------------------------------------
def consultar_container(db: Session, code: str) -> ToolResult:
    """Consulta a ocupação atual de um contêiner."""
    try:
        container = container_service.get_container(db, code)
    except NotFoundError:
        return ToolResult(
            data=None,
            response=f"Não encontrei o contêiner {code}.",
        )

    dados = container.model_dump(mode="json")
    return ToolResult(
        data=dados,
        response=(
            f"O contêiner {container.code} ({container.neighborhood}) está com "
            f"{container.current_fill_level:.1f}% de ocupação — alerta {container.alert_level.value}."
        ),
    )


# ----------------------------------------------------------------------
# listar_pontos_coleta
# ----------------------------------------------------------------------
def listar_pontos_coleta(db: Session) -> ToolResult:
    """Lista os pontos de coleta (contêineres) monitorados."""
    containers = container_service.list_containers(db)
    itens = [
        {
            "code": item.code,
            "neighborhood": item.neighborhood,
            "address": item.address,
            "fill_level": round(item.current_fill_level, 1),
            "alert_level": item.alert_level.value,
            "is_simulated": item.is_simulated,
        }
        for item in containers.items
    ]

    if not itens:
        return ToolResult(
            data={"total": 0, "containers": []}, response="Nenhum ponto de coleta cadastrado."
        )

    if len(itens) == 1:
        resumo = "1 ponto de coleta."
    else:
        criticos = sum(1 for item in itens if item["alert_level"] == "CRITICAL")
        resumo = f"{len(itens)} pontos de coleta (sendo {criticos} em nível crítico)."

    return ToolResult(data={"total": len(itens), "containers": itens}, response=resumo)


# ----------------------------------------------------------------------
# criar_ocorrencia
# ----------------------------------------------------------------------
def criar_ocorrencia(
    db: Session,
    *,
    neighborhood: str,
    category: OccurrenceCategory = OccurrenceCategory.OTHER,
    description: str | None = None,
) -> ToolResult:
    """Cria uma ocorrência a partir do relato do cidadão."""
    try:
        ocorrencia = occurrence_service.create_occurrence(
            db,
            OccurrenceCreate(
                neighborhood=neighborhood,
                description=description,
                reported_category=category,
            ),
        )
    except ConflictError as exc:
        return ToolResult(data=None, response=exc.detail)

    return ToolResult(
        data={
            "protocol": ocorrencia.protocol,
            "status": ocorrencia.status.value,
            "category": ocorrencia.category.value,
            "priority": ocorrencia.priority.value,
            "neighborhood": ocorrencia.neighborhood,
        },
        response=(
            f"Ocorrência registrada com o protocolo {ocorrencia.protocol} para o bairro "
            f"{ocorrencia.neighborhood}."
        ),
    )


# ----------------------------------------------------------------------
# consultar_indicadores
# ----------------------------------------------------------------------
def consultar_indicadores(db: Session) -> ToolResult:
    """Consulta os indicadores do dashboard."""
    dados = dashboard_service.summary(db)
    payload = dados.model_dump(mode="json")

    return ToolResult(
        data=payload,
        response=(
            f"Hoje há {dados.total_occurrences} ocorrência(s) no total, "
            f"{dados.by_status.get('RESOLVED', 0)} resolvida(s) e "
            f"{dados.by_status.get('PENDING_DISPATCH', 0)} aguardando envio."
        ),
    )
