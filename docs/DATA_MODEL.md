# Modelo de dados

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
