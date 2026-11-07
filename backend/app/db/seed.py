"""Seed de demonstração: contêineres, leituras e ocorrências simuladas.

Execução (a partir da pasta `backend/`):

    python -m app.db.seed

Todos os registros criados aqui são dados de demonstração e ficam marcados como
simulados (`is_simulated = true`), conforme a regra de governança do projeto.
As ocorrências passam pelo serviço real de criação e pelas transições de status
reais, para que o seed exercite as mesmas regras da API.
"""

from __future__ import annotations

import logging

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.enums import (
    OccurrenceCategory,
    OccurrenceStatus,
    StatusChangedBy,
    UserRole,
)
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.container import Container
from app.models.occurrence import Occurrence
from app.models.user import User
from app.schemas.container import SensorReadingCreate
from app.schemas.occurrence import OccurrenceCreate, OccurrenceStatusUpdate
from app.services import container_service, occurrence_service

logger = logging.getLogger(__name__)

DEMO_PASSWORD_HASH = "DEMO-ONLY-NOT-A-REAL-HASH"  # autenticação é por cabeçalho nesta fase

DEMO_USERS = [
    ("Administração Smart Clean City", "admin@smartcleancity.demo", UserRole.ADMIN),
    ("Cidadão Demonstração", "cidadao@smartcleancity.demo", UserRole.CITIZEN),
]

# (código, bairro, endereço, latitude, longitude, capacidade, ocupação inicial %)
DEMO_CONTAINERS: list[tuple[str, str, str, float, float, int, float]] = [
    ("CONT-001", "Pinheiros", "Rua dos Pinheiros, 120", -23.5678, -46.6920, 1000, 35.0),
    ("CONT-002", "Vila Madalena", "Rua Harmonia, 45", -23.5545, -46.6890, 1000, 72.0),
    ("CONT-003", "Itaim Bibi", "Av. Brigadeiro Faria Lima, 3000", -23.5850, -46.6820, 1200, 83.0),
    ("CONT-004", "Butantã", "Rua Alvarenga, 800", -23.5710, -46.7210, 1000, 95.0),
    ("CONT-005", "Tatuapé", "Rua Tuiuti, 1500", -23.5400, -46.5760, 800, 88.0),
    ("CONT-006", "Santana", "Av. Voluntários da Pátria, 2000", -23.4980, -46.6250, 1000, 60.0),
]

# (bairro, categoria, descrição, caminho de status desejado, protocolo do portal)
DEMO_OCCURRENCES: list[tuple[str, OccurrenceCategory, str, list[OccurrenceStatus], str]] = [
    (
        "Pinheiros",
        OccurrenceCategory.OVERFLOW,
        "Contêiner transbordando há dois dias na calçada.",
        [
            OccurrenceStatus.PENDING_DISPATCH,
            OccurrenceStatus.DISPATCHED,
            OccurrenceStatus.IN_PROGRESS,
            OccurrenceStatus.RESOLVED,
        ],
        "PORTAL-DEMO-1001",
    ),
    (
        "Vila Madalena",
        OccurrenceCategory.ILLEGAL_DUMPING,
        "Descarte de entulho em terreno vazio.",
        [OccurrenceStatus.PENDING_DISPATCH, OccurrenceStatus.DISPATCHED],
        "PORTAL-DEMO-1002",
    ),
    (
        "Itaim Bibi",
        OccurrenceCategory.DAMAGED_CONTAINER,
        "Contêiner com tampa quebrada e rodas danificadas.",
        [OccurrenceStatus.PENDING_DISPATCH],
        "",
    ),
    (
        "Butantã",
        OccurrenceCategory.OVERFLOW,
        "Ponto de coleta com resíduos espalhados.",
        [OccurrenceStatus.PENDING_DISPATCH, OccurrenceStatus.DISPATCHED],
        "PORTAL-DEMO-1003",
    ),
    (
        "Tatuapé",
        OccurrenceCategory.ILLEGAL_DUMPING,
        "Sacos de lixo descartados ao lado do contêiner.",
        [OccurrenceStatus.REJECTED],
        "",
    ),
    (
        "Santana",
        OccurrenceCategory.OTHER,
        "Registro sem imagem para validação da triagem.",
        [],
        "",
    ),
]


def _seed_users(db: Session) -> int:
    """Cria os perfis de demonstração (autenticação por cabeçalho nesta fase)."""
    existentes = set(db.execute(select(User.email)).scalars().all())
    criados = 0
    for nome, email, papel in DEMO_USERS:
        if email in existentes:
            continue
        db.add(
            User(
                name=nome,
                email=email,
                password_hash=DEMO_PASSWORD_HASH,
                role=papel.value,
            )
        )
        criados += 1
    db.commit()
    return criados


def _seed_containers(db: Session) -> int:
    """Cadastra os contêineres simulados que faltarem."""
    existentes = set(db.execute(select(Container.code)).scalars().all())
    criados = 0
    for codigo, bairro, endereco, lat, lon, capacidade, _ in DEMO_CONTAINERS:
        if codigo in existentes:
            continue
        db.add(
            Container(
                code=codigo,
                neighborhood=bairro,
                address=endereco,
                latitude=lat,
                longitude=lon,
                capacity_liters=capacidade,
                is_simulated=True,
            )
        )
        criados += 1
    db.commit()
    return criados


def _seed_readings(db: Session) -> int:
    """Envia uma leitura inicial por contêiner usando o serviço real de telemetria."""
    from app.models.container import SensorReading

    if db.execute(select(func.count()).select_from(SensorReading)).scalar_one() > 0:
        return 0

    enviadas = 0
    for indice, item in enumerate(DEMO_CONTAINERS, start=1):
        codigo = item[0]
        ocupacao = item[6]
        container_service.register_reading(
            db,
            SensorReadingCreate(
                sensor_id=f"SENSOR-{indice:03d}",
                container_code=codigo,
                fill_level=ocupacao,
                distance_cm=round(max(0.0, 100.0 - ocupacao), 1),
            ),
        )
        enviadas += 1
    return enviadas


def _seed_occurrences(db: Session) -> int:
    """Cria ocorrências de demonstração percorrendo o fluxo real de status."""
    criadas = 0
    for bairro, categoria, descricao, transicoes, portal_protocol in DEMO_OCCURRENCES:
        existente = db.execute(
            select(Occurrence).where(
                Occurrence.neighborhood == bairro,
                Occurrence.description == descricao,
            )
        ).scalar_one_or_none()
        if existente is not None:
            continue

        detalhe = occurrence_service.create_occurrence(
            db,
            OccurrenceCreate(
                neighborhood=bairro,
                description=descricao,
                reported_category=categoria,
            ),
        )

        registro = db.execute(
            select(Occurrence).where(Occurrence.protocol == detalhe.protocol)
        ).scalar_one()
        registro.is_simulated = True
        db.commit()

        for alvo in transicoes:
            occurrence_service.change_status(
                db,
                registro.id,
                OccurrenceStatusUpdate(
                    status=alvo,
                    note="Transição gerada pelo seed de demonstração.",
                ),
                changed_by=StatusChangedBy.SYSTEM,
            )
            if alvo is OccurrenceStatus.DISPATCHED and portal_protocol:
                registro.dispatch_protocol = portal_protocol
                db.commit()

        criadas += 1
    return criadas


def main() -> None:
    """Executa o seed completo e informa o que foi criado."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    init_db()
    with SessionLocal() as db:
        usuarios = _seed_users(db)
        containers = _seed_containers(db)
        leituras = _seed_readings(db)
        ocorrencias = _seed_occurrences(db)
        total_ocorrencias = db.execute(select(func.count()).select_from(Occurrence)).scalar_one()
        total_prioridade = db.execute(
            select(Occurrence.priority, func.count()).group_by(Occurrence.priority)
        ).all()

    logger.info("Usuários criados: %s", usuarios)
    logger.info("Contêineres criados: %s", containers)
    logger.info("Leituras enviadas: %s", leituras)
    logger.info("Ocorrências criadas: %s (total: %s)", ocorrencias, total_ocorrencias)
    logger.info("Distribuição de prioridade: %s", dict(total_prioridade))


if __name__ == "__main__":
    main()
