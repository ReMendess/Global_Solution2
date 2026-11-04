# API_SPEC.md — Contrato REST planejado

> Contrato a ser implementado nas fases 1 a 6. Prefixo base: `/api/v1`. Documentação interativa
> gerada pelo FastAPI em `/docs` e `/redoc`.
> **Status:** nenhuma rota existe ainda (Fase 0).

## 1. Convenções

- JSON em `snake_case` (mesmos nomes das colunas do banco).
- Datas em ISO 8601 UTC (`2026-11-04T12:00:00Z`).
- Paginação por `limit` (padrão 20, máximo 100) e `offset` (padrão 0).
- Erros no formato padrão do FastAPI: `{"detail": "mensagem em pt-BR"}`.
- Códigos: `200` consulta, `201` criação, `204` sem conteúdo, `400` requisição inválida,
  `404` não encontrado, `409` conflito de regra, `422` validação, `500` erro interno.

## 2. Saúde e metadados

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status da API, versão e se o modelo está carregado |
| `GET` | `/api/v1/meta/enums` | Valores canônicos dos enums (consumido pelo frontend) |

Exemplo `GET /health`:

```json
{ "status": "ok", "version": "0.1.0", "database": "ok", "model_loaded": false }
```

## 3. Ocorrências — FASE 1

| Método | Rota | Perfil | Descrição |
|---|---|---|---|
| `POST` | `/api/v1/occurrences` | público | Registra ocorrência com foto (multipart) |
| `GET` | `/api/v1/occurrences` | admin | Lista com filtros |
| `GET` | `/api/v1/occurrences/{id}` | admin | Detalhe por id |
| `GET` | `/api/v1/occurrences/protocol/{protocol}` | público | Consulta de status pelo protocolo |
| `PATCH` | `/api/v1/occurrences/{id}/status` | admin | Altera status com validação de transição |

`POST /api/v1/occurrences` — multipart/form-data:

| Campo | Tipo | Obrigatório | Observação |
|---|---|---|---|
| `neighborhood` | string | sim | 3–120 caracteres |
| `address` | string | não | até 255 caracteres |
| `latitude` | float | não | −90 a 90 |
| `longitude` | float | não | −180 a 180 |
| `description` | string | não | até 1000 caracteres |
| `reporter_name` | string | não | até 120 caracteres |
| `image` | arquivo | não | `image/jpeg` ou `image/png`, ≤ `MAX_UPLOAD_MB` |

Resposta `201`:

```json
{
  "id": 1,
  "protocol": "CL-2026-000001",
  "status": "PENDING_DISPATCH",
  "category": "ILLEGAL_DUMPING",
  "priority": "HIGH",
  "model_label": "IRREGULAR",
  "confidence": 0.91,
  "needs_human_review": false,
  "model_version": "mobilenetv2-v1",
  "created_at": "2026-11-04T12:00:00Z"
}
```

Erros esperados: `409` duplicidade (`dedup_hash`), `422` payload inválido, `413` arquivo grande.

`GET /api/v1/occurrences?status=&category=&priority=&neighborhood=&limit=&offset=` → lista paginada
com `items` e `total`.

## 4. Classificação — FASE 3

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/classification/predict` | Classifica uma imagem isolada (não persiste ocorrência) |
| `GET` | `/api/v1/classification/model-info` | Versão, classes e métricas reais do modelo treinado |

Resposta de `predict`:

```json
{
  "label": "IRREGULAR",
  "confidence": 0.91,
  "probabilities": { "REGULAR": 0.09, "IRREGULAR": 0.91 },
  "model_version": "mobilenetv2-v1",
  "needs_human_review": false
}
```

Se o modelo não estiver carregado: `503` com `detail` explicando que a FASE 3 não foi executada.
A rota **não** é usada no fluxo de criação de ocorrência (que tolera ausência do modelo).

## 5. Contêineres e sensores — FASE 1 e 4

| Método | Rota | Perfil | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/containers` | admin | Lista contêineres com ocupação atual |
| `GET` | `/api/v1/containers/{code}` | público | Detalhe por código |
| `GET` | `/api/v1/containers/{code}/readings` | admin | Histórico paginado de leituras |
| `POST` | `/api/v1/sensors/readings` | interno | Recebe telemetria do simulador |

`POST /api/v1/sensors/readings`:

```json
{ "sensor_id": "SENSOR-001", "container_code": "CONT-001", "fill_level": 92.5, "distance_cm": 12.0 }
```

Resposta `201`:

```json
{
  "id": 10,
  "sensor_id": "SENSOR-001",
  "container_code": "CONT-001",
  "fill_level": 92.5,
  "alert_level": "CRITICAL",
  "is_simulated": true,
  "measured_at": "2026-11-04T12:00:00Z"
}
```
## 6. RPA — FASE 5

| Método | Rota | Perfil | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/rpa/queue` | interno | Demandas elegíveis (`PENDING_DISPATCH`) |
| `POST` | `/api/v1/rpa/executions` | interno | Registra o resultado da automação |
| `GET` | `/api/v1/rpa/executions` | admin | Histórico de execuções |

`GET /api/v1/rpa/queue`:

```json
{
  "total": 1,
  "items": [
    {
      "occurrence_id": 12,
      "protocol": "CL-2026-000012",
      "category": "OVERFLOW",
      "priority": "CRITICAL",
      "neighborhood": "Pinheiros",
      "address": "Rua das Palmeiras, 120",
      "description": "Contêiner transbordando há dois dias"
    }
  ]
}
```

`POST /api/v1/rpa/executions`:

```json
{
  "occurrence_id": 12,
  "status": "SUCCESS",
  "portal_protocol": "PORTAL-8842",
  "duration_ms": 4210,
  "error_message": null
}
```

- `SUCCESS` → ocorrência vai para `DISPATCHED` e grava `dispatch_protocol`.
- `FAILED` → ocorrência permanece `PENDING_DISPATCH` e pode ser reprocessada.
- Segunda execução `SUCCESS` para a mesma ocorrência → `409`.

## 7. Indicadores — FASE 1 (consumo do dashboard na FASE 2)

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/api/v1/dashboard/summary` | Totais por status, categoria e prioridade |
| `GET` | `/api/v1/dashboard/containers` | Contêineres por nível de alerta |
| `GET` | `/api/v1/dashboard/neighborhoods` | Ranking de bairros com mais ocorrências |

Exemplo de `summary`:

```json
{
  "total_occurrences": 42,
  "by_status": { "OPEN": 3, "PENDING_DISPATCH": 8, "DISPATCHED": 20, "RESOLVED": 11 },
  "by_category": { "ILLEGAL_DUMPING": 18, "OVERFLOW": 15, "DAMAGED_CONTAINER": 5, "OTHER": 4 },
  "by_priority": { "LOW": 9, "MEDIUM": 14, "HIGH": 15, "CRITICAL": 4 },
  "needs_human_review": 6,
  "average_resolution_hours": 31.4
}
```

## 8. Agente conversacional — FASE 6

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/api/v1/agent/messages` | Envia mensagem e recebe resposta do agente |
| `GET` | `/api/v1/agent/sessions/{session_id}` | Histórico da sessão |

`POST /api/v1/agent/messages`:

```json
{ "session_id": "sess-abc123", "message": "Qual o status da ocorrência CL-2026-000012?" }
```

Resposta `200`:

```json
{
  "session_id": "sess-abc123",
  "intent": "consultar_ocorrencia",
  "tool_used": "consultar_ocorrencia",
  "response": "A ocorrência CL-2026-000012 está com status DISPATCHED, protocolo do portal PORTAL-8842.",
  "data": { "protocol": "CL-2026-000012", "status": "DISPATCHED" }
}
```

Intenção não reconhecida:

```json
{
  "session_id": "sess-abc123",
  "intent": "desconhecida",
  "tool_used": null,
  "response": "Não entendi. Você pode perguntar, por exemplo: status da ocorrência CL-2026-000012, nível do contêiner CONT-001, ou indicadores do dia.",
  "data": null
}
```

## 9. Mapa rota → fase

| Fase | Rotas |
|---|---|
| 1 (backend) | `/health`, `/api/v1/meta/enums`, `/api/v1/occurrences*`, `/api/v1/containers*`, `/api/v1/dashboard*` |
| 3 (ML) | `/api/v1/classification/*` |
| 4 (IoT) | `POST /api/v1/sensors/readings` |
| 5 (RPA) | `/api/v1/rpa/*` |
| 6 (agente) | `/api/v1/agent/*` |

## 10. Pontos em aberto

1. Autenticação: header demonstrativo na Fase 1 ou JWT desde já?
2. `POST /api/v1/occurrences` aceitar JSON puro (sem arquivo) para o agente criar ocorrências?
   **Proposta:** endpoint separado `POST /api/v1/occurrences/from-agent` na Fase 6.
3. Versionamento: manter `/api/v1` fixo durante todo o projeto (proposta).