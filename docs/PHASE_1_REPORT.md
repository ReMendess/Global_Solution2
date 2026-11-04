# PHASE_1_REPORT.md — Backend, banco e dados simulados

> Relatório de fechamento da FASE 1. Todos os números abaixo foram obtidos por execução real dos
> comandos indicados, não por estimativa.

## 1. Escopo executado

Núcleo FastAPI com persistência real em SQLite: modelos, schemas, regras de negócio, rotas REST,
seed de demonstração e testes automatizados. Nenhuma funcionalidade de fase futura foi antecipada —
o serviço de classificação existe apenas como stub documentado (retorna `None` até a FASE 3).

## 2. Arquivos criados

```
backend/app/__init__.py
backend/app/main.py
backend/app/core/{__init__,config,clock,constants,enums,exceptions}.py
backend/app/db/{__init__,base,session,init_db,seed}.py
backend/app/models/{__init__,user,occurrence,container,automation}.py
backend/app/schemas/{__init__,occurrence,container,dashboard,meta,health}.py
backend/app/services/{__init__,occurrence_service,protocol_service,dedup_service,
                      priority_service,container_service,dashboard_service,
                      storage_service,classification_service}.py
backend/app/api/{__init__,deps}.py
backend/app/api/routes/{__init__,health,meta,occurrences,containers,sensors,dashboard}.py
backend/tests/{conftest,test_health,test_meta,test_services,test_occurrences,
               test_occurrence_management,test_containers,test_dashboard}.py
```

**Modificados:** `backend/tests/test_project_structure.py` (diretório `data/seed` removido),
`.env.example` (`CORS_ORIGINS`), `README.md`, `docs/ROADMAP.md`, `docs/ENVIRONMENT.md`,
`docs/DATA_MODEL.md`, `docs/API_SPEC.md`, `docs/DECISIONS.md`.

**Removidos:** `.gitkeep` de `backend/app/**` (diretórios agora populados) e o diretório `data/seed`
(o seed passou a ser código em `backend/app/db/seed.py`).

## 3. Decisões técnicas tomadas na fase

| Tema | Decisão |
|---|---|
| Caminho do banco | `DATABASE_URL` relativo é resolvido contra a raiz do repositório, então a API funciona igual rodando de `backend/` ou da raiz |
| Seed | Código em `backend/app/db/seed.py` (`python -m app.db.seed`) |
| Seed usa serviços reais | As ocorrências passam por `create_occurrence` e `change_status`, exercitando dedup, prioridade e máquina de estados |
| Classificação | `classification_service` é o único ponto de integração; devolve `None` nesta fase e não bloqueia o registro |
| Perfil de acesso | Cabeçalho `X-User-Role` (`CITIZEN`/`ADMIN`), isolado em `app/api/deps.py` (ADR-014) |
| Revisão humana | Sem modelo, `needs_human_review = true` em toda ocorrência — sinalização honesta |
| `is_simulated` em ocorrências | Coluna adicionada para identificar dados do seed (ADR-015) |
| Datas | UTC sem `tzinfo` (`core/clock.py`) para consistência no SQLite |
| Erros | Exceções de domínio (`AppError` e filhas) traduzidas por handler global |
## 4. Testes executados

```
python -m pytest
89 passed  (backend/tests)
```

Distribuição por arquivo:

| Arquivo | Verificações | Foco |
|---|---|---|
| `test_project_structure.py` | 40 | estrutura, documentação, `.gitignore`, `.env.example` |
| `test_health.py` | 2 | `/health` e `model_loaded` |
| `test_meta.py` | 2 | enums canônicos e estados terminais |
| `test_services.py` | 9 | limiares 80/90, prioridade, revisão humana, hash de dedup |
| `test_occurrences.py` | 9 | criação, protocolo, dedup, upload, formato e limite de imagem |
| `test_occurrence_management.py` | 8 | perfil, filtros, paginação, transições válidas e inválidas |
| `test_containers.py` | 7 | telemetria, limiares, 404/422, histórico, perfil |
| `test_dashboard.py` | 5 | resumo, tempo médio de resolução, alertas, ranking |

## 5. Verificação com a API real (`uvicorn`)

Servidor iniciado em `127.0.0.1:8000` sobre o SQLite `data/cidade_limpa.db`, após o seed:

| Verificação | Resultado real |
|---|---|
| `GET /health` | `{"status":"ok","database":"ok","model_loaded":false}` |
| `GET /api/v1/meta/enums` | 7 status, 4 categorias, 4 prioridades, 3 níveis de alerta |
| `POST /api/v1/occurrences` (com PNG) | `201`, protocolo `CL-2026-000007`, `status=CLASSIFIED`, `priority=HIGH`, imagem de 111 bytes gravada |
| Histórico da ocorrência | `(null → OPEN, CITIZEN)`, `(OPEN → CLASSIFIED, SYSTEM)` |
| `GET /occurrences/protocol/CL-2026-000007` | `200` com os dados persistidos |
| `POST /api/v1/sensors/readings` (93,5%) | `201` com `alert_level=CRITICAL` |
| `GET /api/v1/containers/CONT-001` | `alert_level=CRITICAL` (contêiner atualizado) |
| `GET /api/v1/occurrences` sem `X-User-Role` | `403` |
| `PATCH /api/v1/occurrences/{id}/status` → `DISPATCHED` | `200`, status atualizado e auditoria gravada |
| `GET /api/v1/dashboard/summary` | `total_occurrences=7`, 5 estados em `by_status`, `needs_human_review=7` |
| `GET /api/v1/dashboard/containers` | `CRITICAL: 2`, `HIGH: 2`, `NORMAL: 2`, `critical_codes: [CONT-001, CONT-004]` |
| `GET /api/v1/dashboard/neighborhoods` | 7 bairros, um registro cada |

Seed (`cd backend; python -m app.db.seed`): 2 usuários, 6 contêineres, 6 leituras, 6 ocorrências,
distribuição de prioridade `{HIGH: 3, MEDIUM: 3}`.

## 6. Qualidade

```
python -m ruff check .            -> All checks passed!
python -m ruff format --check .   -> 51 files already formatted
```

## 7. Critérios de aceite — atendidos

- [x] API sobe com `uvicorn app.main:app` a partir de `backend/`
- [x] `GET /health` = `200`
- [x] `POST /api/v1/occurrences` grava ocorrência + imagem + histórico e devolve protocolo
- [x] `GET /api/v1/occurrences/protocol/{protocol}` recupera o registro persistido
- [x] Duplicidade retorna `409` citando o protocolo original
- [x] `GET /api/v1/dashboard/summary` reflete o banco
- [x] `POST /api/v1/sensors/readings` aplica limiares 80/90 e atualiza o contêiner
- [x] `pytest` com todos os testes passando (89)
- [x] `data/cidade_limpa.db` criado e populado pelo seed

## 8. Limitações identificadas

1. **Modelo inexistente nesta fase:** `needs_human_review` fica `true` em toda ocorrência e
   `model_label`/`confidence`/`model_version` permanecem nulos até a FASE 3.
2. **Autenticação demonstrativa:** `X-User-Role` pode ser forjado; sem senha/JWT (revisão na FASE 7).
3. **Sem exclusão de ocorrências:** não previsto no desafio, portanto não implementado.
4. **`average_resolution_hours`:** calculado em Python sobre as linhas resolvidas; com volume alto
   será necessário mover a agregação para SQL.
5. **Uploads:** validação por `content-type` declarado e limite de tamanho; não há verificação
   profunda do conteúdo além da leitura de metadados com Pillow.
6. **Deduplicação por dia:** registros legítimos no mesmo local e dia são bloqueados de propósito;
   a janela é configurável em `core/constants.py`.
7. **OneDrive:** verificado sem processo ativo durante os testes; se voltar a sincronizar, pausar
   (comando em `docs/ENVIRONMENT.md` §7).
8. **Sem `remote` git:** commits locais; o push depende da URL do repositório privado.

## 9. Próximo passo

**FASE 2 — Frontend Expo e dashboard:** projeto Expo com Expo Router + React Native Web consumindo
estas rotas (`/api/v1/meta/enums` para os enums, ocorrências, contêineres e dashboard), com telas de
cidadão e administrador e layout responsivo.

**FASE 3 — observação sobre o treino:** o notebook será executado pelo autor no **Google Colab**
(ADR-013). O Cline entrega o notebook e o pipeline; o treino não roda nesta máquina.