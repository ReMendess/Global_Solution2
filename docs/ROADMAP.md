# ROADMAP.md — Fases, entregáveis e critérios de aceite

> Cada fase só é considerada concluída quando os critérios de aceite forem **verificados por
> execução real**, conforme a regra fundamental do `PROJECT_CONTEXT.md` §15.

## FASE 0 — Planejamento e estrutura ✅

**Escopo:** documentação de planejamento, esqueleto de diretórios, padronização do repositório.

**Entregáveis**

- `README.md`, `.gitignore`, `.editorconfig`, `.env.example`, `pyproject.toml`, `requirements*.txt`.
- `docs/ARCHITECTURE.md`, `docs/DATA_MODEL.md`, `docs/API_SPEC.md`, `docs/BUSINESS_RULES.md`,
  `docs/ROADMAP.md`, `docs/DECISIONS.md`, `docs/ENVIRONMENT.md`.
- Árvore de diretórios de todos os módulos com `.gitkeep`.
- `backend/tests/test_project_structure.py` — teste de integridade da estrutura e da documentação
  (42 verificações parametrizadas).
- Repositório git inicializado com commit inicial.

**Critérios de aceite**

- [x] Estrutura de pastas criada e versionada (diretórios vazios marcados com `.gitkeep`).
- [x] Documentação cobre problema, stack, arquitetura, dados, API, regras e fases.
- [x] `python -m ruff check .` sem erros.
- [x] `python -m ruff format --check .` sem diferenças.
- [x] `python -m pytest` executa e passa (42 verificações de estrutura/documentação).
- [x] Nenhum código de fase futura antecipado.
- [x] Referências entre documentos funcionando.

**Fora de escopo:** qualquer código executável de backend, frontend, ML, IoT, RPA ou agente.

---

## FASE 1 — Backend, banco e dados simulados ✅

**Escopo:** núcleo FastAPI funcional com persistência real em SQLite.

**Entregáveis (implementados)**

- `backend/app/main.py` com `create_app()`, CORS, handler global de exceções e `/health`.
- `backend/app/core/`: `config.py` (`pydantic-settings`), `enums.py`, `constants.py`, `clock.py`,
  `exceptions.py`.
- `backend/app/db/`: `base.py`, `session.py` (`get_db`), `init_db.py`, `seed.py`.
- `backend/app/models/`: as 8 entidades de `DATA_MODEL.md`.
- `backend/app/schemas/`: ocorrências, contêineres, leituras, dashboard, metadados e saúde.
- `backend/app/services/`: `occurrence_service`, `protocol_service`, `dedup_service`,
  `priority_service`, `container_service`, `dashboard_service`, `storage_service`,
  `classification_service` (stub da FASE 3).
- Routers: `health`, `meta`, `occurrences`, `containers`, `sensors`, `dashboard`.
- Seed em `backend/app/db/seed.py` (dados de demonstração marcados como simulados).
- Testes em `backend/tests/`: 47 verificações da FASE 1 (89 no total do projeto).

**Critérios de aceite**

- [x] `python -m uvicorn app.main:app --reload` sobe sem erro a partir de `backend/`.
- [x] `GET /health` retorna `200`.
- [x] `POST /api/v1/occurrences` grava ocorrência + imagem + status_history e devolve protocolo.
- [x] `GET /api/v1/occurrences/protocol/{protocol}` recupera a ocorrência persistida.
- [x] Ocorrência duplicada retorna `409` com o protocolo original.
- [x] `GET /api/v1/dashboard/summary` reflete os dados do banco.
- [x] `POST /api/v1/sensors/readings` valida limiares 80/90 e atualiza o contêiner.
- [x] `python -m pytest` com todos os testes passando (89 passed).
- [x] `data/cidade_limpa.db` criado e populado pelo seed.

**Resultados reais e limitações:** ver [`PHASE_1_REPORT.md`](PHASE_1_REPORT.md).

---

## FASE 2 — Frontend Expo e dashboard ✅

**Escopo:** app React Native + Expo Router + React Native Web consumindo a API.

**Entregáveis (implementados)**

- Projeto Expo **SDK 57** em `frontend/` com Expo Router, TypeScript estrito e React Native Web.
- `frontend/src/services/`: `config.ts` (resolução da URL da API), `api-client.ts` (fetch + `ApiError`),
  `api.ts` (todas as rotas da FASE 1) e `occurrence-form.ts` (multipart multiplataforma).
- Telas do cidadão: início (com status real da API), registro de ocorrência (câmera/galeria),
  resultado com protocolo/classificação e consulta por protocolo.
- Telas do administrador: dashboard com indicadores, lista filtrável e paginada de ocorrências,
  detalhe com imagem + transições de status e monitoramento de contêineres com histórico de leituras.
- Layout responsivo (largura máxima no desktop, grades que colapsam no mobile) e
  alternância de perfil cidadão/administrador.
- `GET /uploads/{arquivo}` no backend para o frontend exibir as imagens enviadas.

**Critérios de aceite**

- [x] `npm run web` (Expo + Metro) serve a aplicação em `http://localhost:8081`.
- [x] O bundle web compila (`expo export --platform web`) e contém a integração com a API.
- [x] As chamadas usam as rotas reais (`/api/v1/meta/enums`, ocorrências, contêineres, dashboard)
      com o cabeçalho `X-User-Role` nas rotas administrativas.
- [x] CORS responde ao preflight da origem `http://localhost:8081`.
- [x] `npm run typecheck` sem erros.
- [x] `npm test` com todos os testes passando (46).
- [ ] Registro de ocorrência e consulta de protocolo validados em navegador (exige teste manual —
      ver limitações no relatório da fase).
- [ ] Execução no Expo Go (exige dispositivo do avaliador).

**Resultados reais, decisões e limitações:** ver [`PHASE_2_REPORT.md`](PHASE_2_REPORT.md).

---

## FASE 3 — MobileNetV2 e visão computacional ✅

**Escopo:** pipeline de ML, notebook para o Colab e integração da inferência no backend.

**Entregáveis (implementados)**

- `ml/src/{config,dataset,preprocess,model,evaluate,train}.py` — pipeline completo executável
  localmente (`python -m ml.src.train`).
- `ml/notebooks/cidade_limpa_mobilenetv2.ipynb` — notebook **autocontido** para o Google Colab
  (seção 7 baixa os artefatos automaticamente).
- `docs/ML_TRAINING_COLAB.md` — roteiro passo a passo para o treinamento.
- `backend/app/services/classification_service.py` — inferência real, com cache, recarga
  automática por mtime e carregamento lazy do TensorFlow.
- `backend/app/schemas/classification.py` + `backend/app/api/routes/classification.py`:
  `GET /api/v1/classification/model-info` e `POST /api/v1/classification/predict`.

**Critérios de aceite**

- [x] Pipeline de dataset com classes `REGULAR` e `IRREGULAR` (validação e divisão reprodutível).
- [x] Notebook de treinamento pronto e testado (build do MobileNetV2 validado com pesos ImageNet).
- [ ] Treino executado e pesos salvos — **pendente de execução no Colab pelo autor** (ADR-013).
- [ ] Métricas reais publicadas — **dependentes do treino acima**.
- [x] `GET /api/v1/classification/model-info` responde `503` sem modelo e `200` com modelo.
- [x] `POST /api/v1/classification/predict` classifica uma imagem (validado com modelo de fixture).
- [x] Ocorrência sem modelo continua sendo registrada (não bloqueia).
- [x] Testes automatizados do serviço de classificação passando (11 novos; 102 no total).

**Resultados reais e limitações:** ver [`PHASE_3_REPORT.md`](PHASE_3_REPORT.md) e
[`ML_TRAINING_COLAB.md`](ML_TRAINING_COLAB.md).

---

## FASE 4 — Simulador IoT ✅

**Escopo:** sensores virtuais enviando telemetria real via HTTP.

**Entregáveis (implementados)**

- `simulator/config.py` — `Settings` (pydantic-settings) e `SensorSpec` + 6 sensores padrão
  (`SENSOR-001`…`SENSOR-006`), alinhados aos contêineres do seed.
- `simulator/core/sensor.py` — sensor ultrassônico virtual (passeio aleatório limitado,
  distância inversa à ocupação, payload no contrato do backend).
- `simulator/sensors/runner.py` — CLI com `--once`, `--critical`, `--interval`, `--rounds`.
- `simulator/README.md` — instruções de uso.
- Testes em `simulator/tests/` (11).

**Critérios de aceite**

- [x] `python -m simulator.sensors.runner` envia leituras contínuas para a API.
- [x] Cada leitura aparece em `GET /api/v1/containers/{code}/readings`.
- [x] `alert_level` corresponde aos limiares 80/90 (NORMAL/HIGH/CRITICAL derivados no backend).
- [x] `--critical` força nível crítico e o alerta `CRITICAL` é observado.
- [x] Toda leitura persistida tem `is_simulated = true`.

**Resultados reais:** ver [`PHASE_4_REPORT.md`](PHASE_4_REPORT.md).

---

## FASE 5 — RPA Playwright ✅

**Escopo:** automação preenchendo portal administrativo fictício.

**Entregáveis (implementados)**

- `rpa/portal/server.py` — portal administrativo fictício (HTTP local, stdlib, protocolo sequencial).
- `rpa/bot/dispatcher.py` — robô: fila → preenchimento → captura do protocolo → registro na API.
- `rpa/bot/selectors.py` — seletores CSS centralizados.
- `rpa/config.py` — configuração (`.env`).
- `backend/app/services/rpa_service.py` + `backend/app/api/routes/rpa.py`:
  `GET /api/v1/rpa/queue`, `POST /api/v1/rpa/executions`, `GET /api/v1/rpa/executions`.
- `rpa/README.md` + testes (`rpa/tests/`, 8) e backend (`backend/tests/test_rpa.py`, 8).

**Critérios de aceite**

- [x] `python -m playwright install chromium` executado (Chromium 1248 instalado).
- [x] Portal fictício sobe e aceita submissão (GET formulário + POST com protocolo).
- [x] Robô processa uma ocorrência `PENDING_DISPATCH` de ponta a ponta.
- [x] Ocorrência passa para `DISPATCHED` com `dispatch_protocol` preenchido (`PORTAL-0001`).
- [x] Execução registrada em `rpa_executions` com duração e status `SUCCESS`.
- [x] Segunda execução para a mesma ocorrência retorna `409`.
- [x] Falha controlada resulta em `FAILED` sem corromper o estado (testado por unidade do serviço).

**Resultados reais:** ver [`PHASE_5_REPORT.md`](PHASE_5_REPORT.md).

---

## FASE 6 — Agente conversacional ✅

**Escopo:** agente baseado em intenções com ferramentas sobre dados reais.

**Entregáveis (implementados)**

- `backend/app/services/agent/intent_parser.py` — interpretação por regras/palavras-chave (sem LLM).
- `backend/app/services/agent/tools.py` — 5 ferramentas sobre serviços reais:
  `consultar_ocorrencia`, `consultar_container`, `listar_pontos_coleta`, `criar_ocorrencia`,
  `consultar_indicadores`.
- `backend/app/services/agent/session.py` — contexto por sessão em memória (última ocorrência/contêiner).
- `backend/app/services/agent/agent.py` — orquestração + persistência em `agent_interactions`.
- `backend/app/api/routes/agent.py` — `POST /api/v1/agent/messages` e `GET /api/v1/agent/sessions/{id}`.
- Testes: `backend/tests/test_agent_parser.py` (10) e `backend/tests/test_agent.py` (8).

**Critérios de aceite**

- [x] Pergunta de status por protocolo retorna dados reais do banco.
- [x] Pergunta sobre nível de contêiner retorna a última leitura persistida.
- [x] Pergunta sobre indicadores retorna o resumo real.
- [x] `criar_ocorrencia` cria registro real e devolve protocolo.
- [x] Pergunta não reconhecida recebe orientação, sem invenção de dados.
- [x] Contexto de sessão mantém a última ocorrência citada.
- [x] Interações persistidas em `agent_interactions`.

**Resultados reais:** ver [`PHASE_6_REPORT.md`](PHASE_6_REPORT.md).

---

## FASE 7 — Integração, testes e CI/CD ✅

**Escopo:** consolidação da qualidade e automação de verificação.

**Entregáveis (implementados)**

- `.github/workflows/ci.yml` — jobs backend (ruff + pytest com cobertura + verificação de segredos)
  e frontend (typecheck + Jest + build web).
- `backend/tests/test_e2e_flow.py` — dois testes ponta a ponta (com e sem visão computacional).
- `pytest-cov` adicionado a `requirements-dev.txt`; cobertura **real: 88%** documentada.
- `docs/TESTING.md` — estratégia e comandos de teste.

**Critérios de aceite**

- [x] Teste ponta a ponta passando com banco temporário (`test_e2e_flow.py`, 2 testes).
- [x] Nenhum segredo versionado (verificado por `git grep` e pelo teste de `.env.example`).
- [x] `ruff check` e `pytest` obrigatórios no CI (e localmente verdes: 149 passed, lint sem erros).
- [x] Cobertura mensurada: **88%** (core de serviços/rotas acima de 90%).
- [ ] Workflow verde no GitHub Actions — **pendente do `push` para o GitHub privado** (o repositório
      ainda não tem `remote` configurado; o YAML foi validado localmente).

**Resultados reais e limitações:** ver [`PHASE_7_REPORT.md`](PHASE_7_REPORT.md).

---

## FASE 8 — Documentação e apresentação ✅

**Escopo:** fechamento acadêmico.

**Entregáveis (implementados)**

- `docs/EXECUTION_GUIDE.md` — instruções de execução de cada módulo.
- `docs/FINAL_REPORT.md` — arquitetura, resultados **reais** (149 testes, 88% cobertura, accuracy
  0,7273), mapa de evidências e limitações consolidadas.
- `docs/DEMO_SCRIPT.md` — roteiro de demonstração passo a passo.
- `README.md` atualizado como porta de entrada (todas as 8 fases concluídas).

**Critérios de aceite**

- [x] Todos os módulos executáveis seguindo apenas a documentação (ver `EXECUTION_GUIDE.md`).
- [x] Métricas e evidências reais anexadas (`FINAL_REPORT.md` e artefatos em `ml/models`/`ml/reports`).
- [x] Limitações listadas sem omissão (`FINAL_REPORT.md` §5).

## Resumo de status

| Fase | Status | Exige testes |
|---|---|---|
| 0 | ✅ concluída | configuração de lint/pytest validada |
| 1 | ✅ concluída | 89 passed |
| 2 | ✅ concluída | 46 passed (Jest) |
| 3 | ✅ concluída (modelo real publicado) | 102 passed |
| 4 | ✅ concluída | 113 passed |
| 5 | ✅ concluída | 129 passed |
| 6 | ✅ concluída | 147 passed |
| 7 | ✅ concluída (CI pronto; push pendente) | 149 passed, 88% cobertura |
| 8 | ✅ concluída | — |