# BUSINESS_RULES.md — Regras de negócio

> Valores canônicos e regras derivadas do `PROJECT_CONTEXT.md` (§6). Estas regras são a fonte única
> para backend, frontend, RPA e agente. Qualquer divergência é bug.

## 1. Categorias de ocorrência

| Valor | Significado |
|---|---|
| `ILLEGAL_DUMPING` | Descarte irregular de resíduos (entulho, lixo em via pública) |
| `OVERFLOW` | Transbordamento de contêiner ou ponto de coleta |
| `DAMAGED_CONTAINER` | Contêiner danificado/inutilizado |
| `OTHER` | Não classificável ou fora das categorias acima |

## 2. Classes do modelo

O modelo classifica a **imagem**, não a ocorrência:

| Valor | Significado |
|---|---|
| `REGULAR` | Situação de descarte regular |
| `IRREGULAR` | Situação irregular detectada |

A categoria é derivada da combinação `model_label` + `confidence` + informação do cidadão. O
`model_label` bruto é sempre persistido para auditoria.

## 3. Status e máquina de estados

```
OPEN ──▶ CLASSIFIED ──▶ PENDING_DISPATCH ──▶ DISPATCHED ──▶ IN_PROGRESS ──▶ RESOLVED
  │            │                  │
  └────────────┴──────────────────┴──────────▶ REJECTED
```

| Transição | Quem dispara | Regra |
|---|---|---|
| `OPEN` → `CLASSIFIED` | Serviço de classificação | Sempre que a imagem é processada (sucesso ou falha do modelo) |
| `CLASSIFIED` → `PENDING_DISPATCH` | Serviço de ocorrências | Quando a categoria é encaminhável |
| `OPEN` → `PENDING_DISPATCH` | Serviço de ocorrências | Atalho quando não há imagem para classificar |
| `PENDING_DISPATCH` → `DISPATCHED` | RPA | Só após `rpa_execution.status = SUCCESS` |
| `DISPATCHED` → `IN_PROGRESS` | Administrador | — |
| `IN_PROGRESS` → `RESOLVED` | Administrador | Exige observação de resolução |
| qualquer → `REJECTED` | Administrador | Exige motivo |

Regras invioláveis:

1. Toda transição grava uma linha em `status_history` (`from_status`, `to_status`, `changed_by`).
2. `RESOLVED` e `REJECTED` são terminais; não voltam para a fila do RPA.
3. Transições fora do diagrama são rejeitadas com `409 Conflict`.

## 4. Prioridades

Cálculo determinístico executado no backend (nunca no frontend):

| Fator | Efeito |
|---|---|
| `model_label = IRREGULAR` e `confidence >= 0.85` | base `HIGH` |
| `model_label = IRREGULAR` e `confidence < 0.70` | base `MEDIUM` + `needs_human_review = true` |
| `model_label = REGULAR` | base `LOW` |
| Modelo indisponível/falhou | base `MEDIUM` + `needs_human_review = true` |
| `category = OVERFLOW` | sobe um nível |
| `category = DAMAGED_CONTAINER` | sobe um nível |
| Contêiner vinculado com `alert_level = CRITICAL` | força `CRITICAL` |
| Prioridade informada pelo cidadão | ignorada (evita manipulação) |

Escala: `LOW < MEDIUM < HIGH < CRITICAL`. “Sobe um nível” nunca ultrapassa `CRITICAL`.

## 5. Alertas de ocupação de contêiner

| Ocupação | `alert_level` |
|---|---|
| menor que 80% | `NORMAL` |
| de 80% até 89% | `HIGH` |
| 90% ou mais | `CRITICAL` |

Regras:

- O limiar é calculado **no backend** a partir de `fill_level`; o simulador envia apenas a medição.
- `fill_level` fora do intervalo `0–100` é rejeitado com `422`.
- Sensor desconhecido → `404`; sensor não associado a contêiner → `422`.
- Toda leitura grava `is_simulated = true` (não existe sensor físico neste projeto).
## 6. Modelo de Machine Learning

- O modelo **não pode impedir** o registro de uma ocorrência. Falha de inferência → ocorrência
  persiste com `category = OTHER` e `needs_human_review = true`.
- `confidence < CONFIDENCE_THRESHOLD` (padrão `0.70`) → `needs_human_review = true`.
- `model_version` é sempre gravado junto com `model_label` e `confidence`.
- Métricas divulgadas devem vir de execução real (accuracy, precision, recall, F1, matriz de
  confusão). **Nenhum resultado pode ser estimado ou inventado.**

## 7. Encaminhamento via RPA

1. Só são elegíveis ocorrências em `PENDING_DISPATCH`.
2. Cada ocorrência pode ter no máximo **uma** execução `SUCCESS` (controle contra duplicidade).
3. O robô deve capturar o protocolo do portal e devolvê-lo à API; sem protocolo, a execução é
   `FAILED`.
4. Toda execução é registrada em `rpa_executions` com início, fim, duração e evidência.
5. `POST /rpa/executions` só é aceito para ocorrências em `PENDING_DISPATCH`; caso contrário `409`.

## 8. Agente conversacional

- Interpretação por intenções + regras; **sem LLM externo**.
- Ferramentas: `consultar_ocorrencia`, `consultar_container`, `listar_pontos_coleta`,
  `criar_ocorrencia`, `consultar_indicadores`.
- Toda resposta deve derivar de dados persistidos. Sem dado disponível, a resposta deve declarar isso.
- Intenção não reconhecida → resposta de orientação com exemplos de perguntas válidas.
- Contexto por sessão: guarda a última ocorrência/contêiner citado para permitir continuidade.
- Toda interação é persistida em `agent_interactions`.

## 9. Segurança e governança

| Regra | Como é aplicada |
|---|---|
| Validar entradas | Schemas Pydantic em todas as rotas; `422` em payload inválido |
| Controlar acesso por perfil | Perfil `ADMIN` exigido nas rotas administrativas |
| Minimizar dados pessoais | Sem CPF, telefone ou endereço completo obrigatório |
| Proteger imagens identificáveis | Upload restrito a imagem; nome de arquivo gerado pelo servidor |
| Identificar dados simulados | Flags `is_simulated` em imagens, contêineres e leituras |
| Registrar execuções do RPA | Tabela `rpa_executions` |
| Registrar resultado e versão do modelo | `model_label`, `confidence`, `model_version` |
| Evitar duplicidade | `dedup_hash` (ver `DATA_MODEL.md` §5) |
| Não expor credenciais | Apenas `.env` (ignorado) + `.env.example` |
| Tratar exceções | Handler global; `500` genérico ao cliente e log detalhado no servidor |

## 10. Ambiguidades que exigem decisão na FASE 1

1. Categoria `OTHER`: encaminhar ou deixar em revisão manual?
   **Proposta:** `OTHER` não entra na fila do RPA e recebe `needs_human_review = true`.
2. Autenticação real (JWT) ou perfil demonstrativo por header?
   **Proposta:** header simples na Fase 1, revisado na Fase 7.
3. Exclusão de ocorrências: não prevista no desafio → **não será implementada**.