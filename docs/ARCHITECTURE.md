# ARCHITECTURE.md — Arquitetura do Smart Clean City

> Documento derivado de [`PROJECT_CONTEXT.md`](PROJECT_CONTEXT.md). Define componentes, fronteiras,
> fluxos e critérios estruturais. Nenhuma implementação é descrita aqui; apenas o desenho acordado.

## 1. Princípio central

O **backend FastAPI é o núcleo único**. Todo módulo (frontend, simulador, RPA, agente) conversa com
ele exclusivamente via **HTTP/JSON**. Não existe acesso direto ao banco por nenhum outro componente.
Isso garante rastreabilidade, um único ponto de validação de entrada e um único ponto de auditoria.

```
                        ┌────────────────────────────────────────────┐
                        │            FastAPI (núcleo)                │
   ┌──────────────┐     │  ┌──────────┐  ┌───────────┐  ┌──────────┐ │
   │  Frontend    │────▶│  │ Routers  │─▶│ Services  │─▶│  Models  │ │
   │ Expo / RN Web│◀────│  │ (REST)   │◀─│ (regras)  │◀─│ SQLAlchemy│ │
   └──────────────┘     │  └──────────┘  └───────────┘  └────┬─────┘ │
                        │        ▲             │              │       │
   ┌──────────────┐     │        │             ▼              ▼       │
   │  Simulador   │────▶│  ┌─────┴─────┐  ┌─────────┐   ┌───────────┐ │
   │  IoT (ESP32) │     │  │  Schemas  │  │ Serviço │   │  SQLite   │ │
   └──────────────┘     │  │ Pydantic  │  │   ML    │   │  (disco)  │ │
                        │  └───────────┘  └────┬────┘   └───────────┘ │
   ┌──────────────┐     │                      │                     │
   │  RPA (Playwright)│─│──────────────────────┘                     │
   └──────┬───────┘     └────────────────────────────────────────────┘
          │                                  ▲
          ▼                                  │
   ┌──────────────┐                  ┌───────┴──────┐
   │   Portal     │                  │   Agente     │
   │ administrativo│                 │ (intenções)  │
   │  fictício    │                  └──────────────┘
   └──────────────┘
```

## 2. Componentes e responsabilidades

| Componente | Responsabilidade | Não faz |
|---|---|---|
| `backend/app/api/routes` | Expor endpoints REST, validar entrada, traduzir erros em HTTP | Não contém regra de negócio |
| `backend/app/services` | Regras de negócio, classificação ML, disparo/registro do RPA, ferramentas do agente | Não monta resposta HTTP |
| `backend/app/models` | Mapeamento SQLAlchemy das 8 entidades | Não valida payload |
| `backend/app/schemas` | Contratos Pydantic de entrada e saída | Não acessa o banco |
| `backend/app/core` | Settings (via `pydantic-settings`), enums canônicos, constantes de limiar | Não persiste dados |
| `backend/app/db` | Engine, sessionmaker, `get_db`, inicialização de schema | Não contém lógica de domínio |
| `frontend/` | Interface responsiva cidadão + administrador, consumindo apenas a API | Não conhece o banco |
| `ml/` | Preparação de dataset, treino, avaliação, geração de pesos e metadados | Não serve requisições |
| `simulator/` | Sensores virtuais enviando leituras HTTP/JSON ao backend | Não escreve no banco |
| `rpa/` | Portal fictício + robô Playwright que preenche e protocola demandas | Não altera o banco |
| agente (no backend) | Interpretar intenção, chamar ferramentas que leem a API, manter contexto de sessão | Não inventa dados, não usa LLM externo |

## 3. Fronteiras e contratos

1. **Frontend ⇄ Backend:** REST/JSON. Nenhuma regra crítica no cliente (ex.: cálculo de prioridade é
   sempre do backend).
2. **Simulador ⇄ Backend:** `POST /api/v1/sensors/readings` com identificador do sensor, nível de
   ocupação e timestamp. O backend deriva o status do alerta.
3. **Backend ⇄ ML:** chamada interna de serviço (`services/classification`). O modelo nunca é
   carregado pelo frontend nem pelo RPA.
4. **RPA ⇄ Backend:** o robô consulta a fila (`GET /api/v1/rpa/queue`), preenche o portal fictício e
   devolve o resultado (`POST /api/v1/rpa/executions`). O robô **não** grava direto no banco.
5. **Agente ⇄ Backend:** usa as mesmas funções de serviço que os routers usam, garantindo que a
   resposta reflita dados persistidos.

## 4. Fluxo ponta a ponta (ocorrência)

```
[1] Cidadão envia foto + bairro + localização
      → Frontend: POST /api/v1/occurrences (multipart)
[2] Backend valida o payload com Pydantic
      → grava Occurrence (status OPEN) + OccurrenceImage
      → StatusHistory: OPEN
[3] Backend chama o serviço de classificação (MobileNetV2)
      → grava model_label, confidence, category, priority
      → StatusHistory: CLASSIFIED → PENDING_DISPATCH
      → devolve o protocolo ao cidadão (nunca bloqueia o registro)
[4] RPA lê GET /api/v1/rpa/queue (demandas elegíveis)
      → abre o portal administrativo fictício
      → preenche os dados da ocorrência e submete
      → captura o protocolo do portal
      → POST /api/v1/rpa/executions com sucesso/erro
[5] Backend atualiza a ocorrência para DISPATCHED
      → StatusHistory: DISPATCHED (com o número protocolado)
```

Observação: a classificação **nunca** bloqueia o registro. Se o modelo falhar, a ocorrência é
persistida com categoria `OTHER` e sinalizada para revisão humana.

## 5. Fluxo ponta a ponta (telemetria)

```
Sensor virtual → POST /api/v1/sensors/readings → valida sensor e contêiner
             → grava SensorReading (com flag simulated=true)
             → calcula alerta (NORMAL / HIGH / CRITICAL) por limiar
             → atualiza nível atual do Container
             → resposta 201 com o alerta derivado
```

## 6. Decisões estruturais

| # | Decisão | Justificativa | Consequência |
|---|---|---|---|
| A1 | Monorepo com pastas por domínio | Um único entregável acadêmico, fácil de avaliar | Scripts por módulo, sem pacote Python instalável |
| A2 | REST-only entre frontend e backend | Exigência do desafio | Nenhum estado compartilhado no cliente |
| A3 | SQLite único em `data/` | Simplicidade e persistência real | Sem concorrência alta; `check_same_thread=False` na Fase 1 |
| A4 | Sem Alembic | MVP acadêmico, schema criado por `create_all()` | Mudanças de schema exigem recriar o banco (aceitável e documentado) |
| A5 | Serviços como camada de regra | Routers finos, agente reutiliza as mesmas funções | Testes de regra sem HTTP |
| A6 | Uploads em disco + caminho no banco | Evita BLOB no SQLite | `UPLOAD_DIR` configurável, arquivos fora do git |
| A7 | Enums em `core/enums.py` | Fonte única para API, banco e frontend | Frontend replica os valores em tipos TS na Fase 2 |
| A8 | Portal administrativo fictício servido local | Demonstração do RPA sem depender de sistema externo | Porta dedicada (8100) separada da API (8000) |

## 7. Tratamento de erros e observabilidade

- Erros de validação → `422` (Pydantic nativo).
- Recurso inexistente → `404` com `detail` em pt-BR.
- Conflito de regra (ex.: duplicidade de dispatch) → `409`.
- Falha interna inesperada → `500` com mensagem genérica ao cliente e log detalhado no servidor.
- Falha do modelo ML → não é erro para o usuário: registra `model_status=FAILED` e segue o fluxo.
- Toda execução do RPA e toda interação do agente são persistidas (auditoria).

## 8. O que este documento exclui

Não define schema de colunas (ver [`DATA_MODEL.md`](DATA_MODEL.md)), rotas detalhadas (ver
[`API_SPEC.md`](API_SPEC.md)) nem critérios de aceite por fase (ver [`ROADMAP.md`](ROADMAP.md)).