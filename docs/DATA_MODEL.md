# DATA_MODEL.md — Modelo de dados planejado

> Projeto de schema para a FASE 1. Nenhuma tabela é criada nesta fase; este documento é o contrato a
> ser implementado com SQLAlchemy 2.0 em `backend/app/models/`.

## 1. Convenções

- Nomes de tabelas e colunas em `snake_case` e **inglês** (alinhado ao `PROJECT_CONTEXT.md`).
- Chave primária: `id` inteiro autoincremental em todas as tabelas.
- Datas em UTC, armazenadas como `DATETIME`, campos `created_at` / `updated_at`.
- Enums persistidos como `VARCHAR` (valores canônicos em maiúsculas), não como `Enum` nativo do
  SQLite, para permitir evolução do conjunto sem migração destrutiva.
- Nenhum campo guarda dado pessoal além do mínimo necessário (`reporter_name` é opcional).
- Nada de BLOB de imagem: as fotos ficam em `UPLOAD_DIR` e o banco guarda o caminho relativo.

## 2. Enums canônicos

| Enum | Valores |
|---|---|
| `OccurrenceCategory` | `ILLEGAL_DUMPING`, `OVERFLOW`, `DAMAGED_CONTAINER`, `OTHER` |
| `ModelLabel` | `REGULAR`, `IRREGULAR` |
| `OccurrenceStatus` | `OPEN`, `CLASSIFIED`, `PENDING_DISPATCH`, `DISPATCHED`, `IN_PROGRESS`, `RESOLVED`, `REJECTED` |
| `Priority` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `AlertLevel` | `NORMAL`, `HIGH`, `CRITICAL` |
| `UserRole` | `CITIZEN`, `ADMIN` |
| `RPAStatus` | `SUCCESS`, `FAILED`, `SKIPPED` |

Detalhamento das regras em [`BUSINESS_RULES.md`](BUSINESS_RULES.md).

## 3. Entidades

### 3.1 `users`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `name` | String(120) | not null | Nome de exibição |
| `email` | String(255) | unique, not null | Identificação de login (dado mínimo) |
| `password_hash` | String(255) | not null | Hash, nunca senha em texto |
| `role` | String(20) | not null, default `CITIZEN` | `CITIZEN` ou `ADMIN` |
| `created_at` | DateTime | not null | — |

Relações: `1..N` com `occurrences`; `1..N` com `agent_interactions`.

### 3.2 `occurrences`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `protocol` | String(32) | unique, not null, index | Protocolo público (ex.: `CL-2026-000123`) |
| `user_id` | Integer | FK `users.id`, nullable | Nulo quando o registro é anônimo (RPA/agente) |
| `category` | String(30) | not null, default `OTHER` | Categoria final da ocorrência |
| `description` | Text | nullable | Relato livre do cidadão |
| `neighborhood` | String(120) | not null, index | Bairro informado |
| `address` | String(255) | nullable | Logradouro/referência |
| `latitude` | Float | nullable | Coordenada |
| `longitude` | Float | nullable | Coordenada |
| `status` | String(30) | not null, default `OPEN`, index | Ver máquina de estados |
| `priority` | String(20) | not null, default `MEDIUM`, index | Calculada pelo backend |
| `model_label` | String(20) | nullable | `REGULAR` / `IRREGULAR` retornado pelo modelo |
| `confidence` | Float | nullable | 0.0–1.0 |
| `needs_human_review` | Boolean | not null, default `False` | `True` quando `confidence < CONFIDENCE_THRESHOLD` |
| `model_version` | String(60) | nullable | Versão dos pesos usados na inferência |
| `dispatch_protocol` | String(60) | nullable | Protocolo devolvido pelo portal via RPA |
| `dedup_hash` | String(64) | index | Hash de deduplicação (ver §5) |
| `is_simulated` | Boolean | not null, default `False` | `True` para registros do seed (ADR-015) |
| `created_at` | DateTime | not null, index | — |
| `updated_at` | DateTime | not null | — |

Relações: `N..1` `users`; `1..N` `occurrence_images`; `1..N` `status_history`; `1..N`
`rpa_executions`.

### 3.3 `occurrence_images`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `occurrence_id` | Integer | FK `occurrences.id`, not null, index | — |
| `file_path` | String(255) | not null | Caminho relativo em `UPLOAD_DIR` |
| `content_type` | String(60) | not null | Ex.: `image/jpeg` |
| `size_bytes` | Integer | not null | Tamanho do arquivo |
| `width` | Integer | nullable | Dimensão após normalização |
| `height` | Integer | nullable | Dimensão após normalização |
| `is_simulated` | Boolean | not null, default `False` | Marca imagem de demonstração |
| `created_at` | DateTime | not null | — |

### 3.4 `containers`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `code` | String(40) | unique, not null, index | Identificador urbano (ex.: `CONT-001`) |
| `neighborhood` | String(120) | not null, index | — |
| `address` | String(255) | nullable | — |
| `latitude` | Float | nullable | — |
| `longitude` | Float | nullable | — |
| `capacity_liters` | Integer | not null, default 1000 | Capacidade nominal |
| `current_fill_level` | Float | not null, default 0.0 | Última ocupação em % |
| `alert_level` | String(20) | not null, default `NORMAL`, index | Derivado da ocupação |
| `is_simulated` | Boolean | not null, default `True` | Contêiner de demonstração |
| `last_reading_at` | DateTime | nullable | Momento da última leitura |
| `created_at` | DateTime | not null | — |

Relações: `1..N` `sensor_readings`.

### 3.5 `sensor_readings`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `sensor_id` | String(40) | not null, index | Identificador do sensor virtual (ESP32) |
| `container_id` | Integer | FK `containers.id`, not null, index | — |
| `fill_level` | Float | not null | 0–100 (%) |
| `distance_cm` | Float | nullable | Leitura do ultrassônico virtual |
| `alert_level` | String(20) | not null | Derivado no backend |
| `is_simulated` | Boolean | not null, default `True` | Sempre verdadeiro neste projeto |
| `measured_at` | DateTime | not null, index | Data/hora da leitura |
| `created_at` | DateTime | not null | — |

Índice composto sugerido: `(container_id, measured_at)` para histórico.
### 3.6 `rpa_executions`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `occurrence_id` | Integer | FK `occurrences.id`, not null, index | Demanda processada |
| `status` | String(20) | not null, index | `SUCCESS` / `FAILED` / `SKIPPED` |
| `portal_protocol` | String(60) | nullable | Protocolo lido no portal |
| `attempt` | Integer | not null, default 1 | Tentativa (controle de duplicidade) |
| `error_message` | Text | nullable | Detalhe da falha |
| `screenshot_path` | String(255) | nullable | Evidência da execução |
| `started_at` | DateTime | not null | — |
| `finished_at` | DateTime | nullable | — |
| `duration_ms` | Integer | nullable | Tempo total |

Restrição de negócio: no máximo **uma** execução `SUCCESS` por `occurrence_id` (§5).

### 3.7 `agent_interactions`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `session_id` | String(64) | not null, index | Contexto simples por sessão |
| `user_id` | Integer | FK `users.id`, nullable | Nulo em sessão anônima |
| `intent` | String(60) | not null, index | Intenção reconhecida |
| `message` | Text | not null | Pergunta do usuário |
| `response` | Text | not null | Resposta gerada a partir de dados reais |
| `tool_used` | String(60) | nullable | Ferramenta acionada |
| `tool_payload` | Text | nullable | JSON com o resultado resumido da ferramenta |
| `created_at` | DateTime | not null, index | — |

### 3.8 `status_history`

| Coluna | Tipo | Restrições | Descrição |
|---|---|---|---|
| `id` | Integer | PK | — |
| `occurrence_id` | Integer | FK `occurrences.id`, not null, index | — |
| `from_status` | String(30) | nullable | Nulo na transição inicial |
| `to_status` | String(30) | not null | Novo estado |
| `note` | String(255) | nullable | Motivo/observação |
| `changed_by` | String(30) | not null, default `SYSTEM` | `CITIZEN` / `ADMIN` / `RPA` / `AGENT` / `SYSTEM` |
| `created_at` | DateTime | not null, index | — |

## 4. Relacionamentos

```
users       1 ──< occurrences
occurrences 1 ──< occurrence_images
occurrences 1 ──< status_history
occurrences 1 ──< rpa_executions
containers  1 ──< sensor_readings
users       1 ──< agent_interactions
```

- `occurrences.user_id` é opcional: ocorrências criadas pelo agente ou importadas não têm autor
  autenticado.
- `occurrence_images` é `1..N` para permitir múltiplas fotos no futuro, mas a FASE 1 grava 1 foto.
## 5. Deduplicação e integridade

**Deduplicação de ocorrência (evitar duplicidade de registro):**

```
dedup_hash = sha256(neighborhood | category | round(latitude,4) | round(longitude,4) | YYYY-MM-DD)
```

- A deduplicação **só é aplicada quando há coordenadas** (latitude e longitude).
- **Sem coordenadas**, a API não bloqueia o registro: dois bairros podem ter varias ocorrências
  distintas no mesmo dia (o bairro é grande demais para deduplicar sem localização).
- Antes de inserir, o serviço calcula o hash e verifica se existe ocorrência com o mesmo hash e
  status diferente de `RESOLVED`/`REJECTED` nas últimas 24 horas.
- Se existir, a API responde `409 Conflict` com o `protocol` original e a mensagem
  “Já existe uma ocorrência aberta para este local hoje”.
- O hash é armazenado para consulta (como `NULL` quando não há coordenadas) e nunca é recalculado a
  partir de dados mutáveis.

**Deduplicação de dispatch (RPA):**

- `rpa_executions` aceita múltiplas tentativas `FAILED`, mas apenas uma `SUCCESS` por ocorrência.
- A fila (`GET /api/v1/rpa/queue`) só devolve ocorrências em `PENDING_DISPATCH`; ao mudar para
  `DISPATCHED` a ocorrência deixa de ser elegível, impedindo reprocessamento.
- Tentativa duplicada recebe `409` com o protocolo já existente.

## 6. Índices planejados

| Tabela | Índice | Motivo |
|---|---|---|
| `occurrences` | `protocol` (unique), `status`, `category`, `priority`, `created_at`, `dedup_hash` | Filtros do dashboard e consulta por protocolo |
| `occurrences` | `neighborhood` | Indicadores por bairro |
| `sensor_readings` | `(container_id, measured_at)` | Histórico de ocupação |
| `agent_interactions` | `session_id`, `created_at` | Contexto de sessão e histórico |
| `rpa_executions` | `occurrence_id`, `status` | Controle de duplicidade e relatório |

## 7. Estratégia de criação do schema

- `backend/app/db/base.py`: `Base` declarativa do SQLAlchemy 2.0.
- `backend/app/db/session.py`: engine com `connect_args={"check_same_thread": False}` e `get_db()`.
- `backend/app/db/init_db.py`: `Base.metadata.create_all(engine)` no startup da aplicação e no script
  de seed.
- Sem Alembic (decisão A4 em [`ARCHITECTURE.md`](ARCHITECTURE.md)).
- Seed de demonstração em `backend/app/db/seed.py` (`python -m app.db.seed`), marcando
  `is_simulated=True` em contêineres, leituras e ocorrências demonstrativas.

## 8. Pendências da FASE 1 — resolvidas na implementação

1. **Regra de prioridade:** confirmada e implementada em
   `backend/app/services/priority_service.py`, exatamente conforme
   [`BUSINESS_RULES.md`](BUSINESS_RULES.md) §4 (com `HIGH_CONFIDENCE = 0.85`).
2. **Seed de `users`:** decidido — dois perfis demonstrativos
   (`admin@cidadelimpa.demo` / `cidadao@cidadelimpa.demo`). A autenticação é por cabeçalho
   `X-User-Role` nesta fase (ADR-014), então `password_hash` guarda apenas um marcador.
3. **`dedup_hash`:** validado em teste automatizado (mesmo bairro/coordenadas no mesmo dia → `409`;
   bairro diferente → registro aceito). A janela é de 24 h e ignora ocorrências terminais.
4. **Ocorrências com `needs_human_review`:** enquanto o modelo não existe (FASE 1), toda ocorrência
   fica sinalizada para revisão — comportamento correto, não um defeito.