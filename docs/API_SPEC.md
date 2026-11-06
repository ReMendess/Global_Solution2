# API_SPEC.md — Contrato REST planejado

> Contrato REST. Prefixo base: `/api/v1`. Documentação interativa gerada pelo FastAPI em `/docs`.
> **Status:** FASE 1 e FASE 3 implementadas e verificadas (saúde, metadados, ocorrências,
> contêineres, sensores, dashboard e classificação). Rotas do RPA e do agente entram nas fases 5 e 6.

## 1. Convenções

- JSON em `snake_case` (mesmos nomes das colunas do banco).
- Datas em ISO 8601 UTC sem timezone (`2026-11-04T12:00:00`).
- Paginação por `limit` (padrão 20, máximo 100) e `offset` (padrão 0).
- Erros no formato padrão do FastAPI: `{"detail": "mensagem em pt-BR"}`.
- Códigos: `200` consulta, `201` criação, `400` requisição inválida, `403` perfil sem permissão,
  `404` não encontrado, `409` conflito de regra, `413` arquivo grande, `422` validação,
  `500` erro interno.
- **Perfil de acesso:** cabeçalho `X-User-Role` com `CITIZEN` (padrão) ou `ADMIN`. Rotas
  administrativas exigem `ADMIN` e respondem `403` sem ele.

## 2. Saúde e metadados

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/health` | Status da API, versão e se o modelo está carregado |
| `GET` | `/api/v1/meta/enums` | Valores canônicos dos enums (consumido pelo frontend) |
| `GET` | `/uploads/{arquivo}` | Serve as imagens enviadas (`data/uploads`); usado pelo frontend |

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
| `reported_category` | enum | não | Categoria informada pelo cidadão; a IA confirma na FASE 3 |
| `image` | arquivo | não | `image/jpeg` ou `image/png`, ≤ `MAX_UPLOAD_MB` |

Resposta `201` (resumo; o corpo completo inclui `images`, `status_history` e `is_simulated`):

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
  "is_simulated": false,
  "images": [
    {
      "file_path": "5f6dae6553cf42a7be958ef98ae2002a.png",
      "content_type": "image/png",
      "size_bytes": 111,
      "width": 32,
      "height": 32,
      "is_simulated": false
    }
  ],
  "status_history": [
    { "from_status": null, "to_status": "OPEN", "changed_by": "CITIZEN" },
    { "from_status": "OPEN", "to_status": "CLASSIFIED", "changed_by": "SYSTEM" },
    { "from_status": "CLASSIFIED", "to_status": "PENDING_DISPATCH", "changed_by": "SYSTEM" }
  ]
}
```

Comportamento real na FASE 1 (modelo ainda inexistente): a ocorrência é gravada com
`needs_human_review: true` e `model_label: null`. Com foto o status vai para `CLASSIFIED`; sem foto,
permanece em `OPEN`. O status só chega a `PENDING_DISPATCH` quando a classificação existir (FASE 3)
ou quando o administrador aprovar a revisão via `PATCH /occurrences/{id}/status`.

Erros esperados: `409` duplicidade (`dedup_hash`), `422` payload inválido, `413` arquivo grande.

`GET /api/v1/occurrences?status=&category=&priority=&neighborhood=&limit=&offset=` → lista paginada
com `items` e `total`.

## 4. Classificação — FASE 3 ✅

| Método | Rota | Perfil | Descrição |
|---|---|---|---|
| `POST` | `/api/v1/classification/predict` | público | Classifica uma imagem isolada (não persiste ocorrência) |
| `GET` | `/api/v1/classification/model-info` | público | Versão, classes e métricas **reais** do modelo treinado |

`POST /api/v1/classification/predict` recebe `multipart/form-data` com o campo `image`
(`image/jpeg` ou `image/png`, ≤ `MAX_UPLOAD_MB`).

Resposta `200`:

```json
{
  "label": "IRREGULAR",
  "confidence": 0.91,
  "probabilities": { "REGULAR": 0.09, "IRREGULAR": 0.91 },
  "model_version": "mobilenetv2-v1",
  "needs_human_review": false
}
```

`GET /api/v1/classification/model-info` devolve os metadados gerados no treinamento
(versão, classes, `image_size` e as métricas reais calculadas no conjunto de teste).

Comportamento sem modelo publicado:

- `GET /model-info` → `503` com orientação para treinar e publicar os pesos;
- `POST /predict` → `503`;
- arquivo fora de JPEG/PNG ou ilegível → `422`;
- arquivo acima do limite → `413`.

A rota de diagnóstico **não** é usada no fluxo de criação de ocorrência: este chama o
serviço internamente e **tolera ausência/falha do modelo** (registro nunca é bloqueado).

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
## 6. RPA — FASE 5 ✅

| Método | Rota | Perfil | Descrição |
|---|---|---|---|
| `GET` | `/api/v1/rpa/queue` | interno | Demandas elegíveis (`PENDING_DISPATCH`), ordenadas por prioridade |
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
- `FAILED` → ocorrência permanece `PENDING_DISPATCH` e pode ser reprocessada (o `attempt`
  é incrementado a cada tentativa).
- Segunda execução `SUCCESS` para a mesma ocorrência → `409`.
- `SUCCESS` sem `portal_protocol` → `409`.
- A ocorrência sai da fila assim que é despachada (deixa de estar em `PENDING_DISPATCH`).

A fila também devolve o `status` da ocorrência e as execuções devolvem `attempt`, `started_at`,
`finished_at` e `duration_ms`.

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

## 8. Agente conversacional — FASE 6 ✅

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