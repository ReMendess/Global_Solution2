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

## FASE 1 — Backend, banco e dados simulados

**Escopo:** núcleo FastAPI funcional com persistência real em SQLite.

**Entregáveis**

- `backend/app/main.py` com `create_app()`, CORS, handler global de exceções e `/health`.
- `backend/app/core/`: `config.py` (`pydantic-settings`), `enums.py`, `constants.py` (limiares).
- `backend/app/db/`: `base.py`, `session.py` (`get_db`), `init_db.py`.
- `backend/app/models/`: as 8 entidades de `DATA_MODEL.md`.
- `backend/app/schemas/`: entrada/saída de ocorrências, contêineres, leituras e indicadores.
- `backend/app/services/`: `occurrence_service`, `protocol_service`, `dedup_service`,
  `container_service`, `dashboard_service`.
- Routers: `occurrences`, `containers`, `dashboard`, `meta`, `health`.
- Seed em `data/seed/seed.py` (contêineres e ocorrências demonstrativas marcadas como simuladas).
- Testes em `backend/tests/`: criação de ocorrência, consulta por protocolo, filtros, deduplicação,
  transição de status inválida, limiares de alerta e `/health`.

**Critérios de aceite**

- [ ] `uvicorn app.main:app --reload` sobe sem erro a partir de `backend/`.
- [ ] `GET /health` retorna `200`.
- [ ] `POST /api/v1/occurrences` grava ocorrência + imagem + status_history e devolve protocolo.
- [ ] `GET /api/v1/occurrences/protocol/{protocol}` recupera a ocorrência persistida.
- [ ] Ocorrência duplicada retorna `409` com o protocolo original.
- [ ] `GET /api/v1/dashboard/summary` reflete os dados do banco.
- [ ] `POST /api/v1/sensors/readings` valida limiares 80/90 e atualiza o contêiner.
- [ ] `python -m pytest` com todos os testes passando.
- [ ] `data/cidade_limpa.db` criado e populado pelo seed.

---

## FASE 2 — Frontend Expo e dashboard

**Escopo:** app React Native + Expo Router + React Native Web consumindo a API.

**Entregáveis**

- Projeto Expo em `frontend/` com Expo Router e TypeScript.
- Camada `services/api.ts` (único ponto de acesso HTTP).
- Telas do cidadão: home, registro de ocorrência (câmera/galeria), resultado com classificação,
  consulta por protocolo e chat do agente.
- Telas do administrador: login demonstrativo, dashboard com indicadores, lista filtrável de
  ocorrências, detalhe com imagem, contêineres, histórico de sensores e execuções do RPA.
- Layout responsivo (grid adaptativo para desktop e mobile).

**Critérios de aceite**

- [ ] `npx expo start --web` abre a aplicação no navegador.
- [ ] Registro de ocorrência pela web cria registro real na API.
- [ ] Consulta por protocolo exibe o status vindo do banco.
- [ ] Dashboard mostra os números retornados por `/api/v1/dashboard/summary`.
- [ ] Filtros de ocorrência por categoria e status funcionam.
- [ ] App executa no Expo Go (mobile) apontando para a API.
- [ ] Testes de frontend executam com sucesso.
---

## FASE 3 — MobileNetV2 e visão computacional

**Escopo:** modelo realmente treinado e integrado ao backend.

**Entregáveis**

- `ml/src/dataset.py`, `ml/src/preprocess.py`, `ml/src/train.py`, `ml/src/evaluate.py`.
- Notebook de treinamento em `ml/notebooks/`.
- Pesos em `ml/models/cidade_limpa_mobilenetv2.keras` + metadados JSON.
- Relatório real em `ml/reports/` (accuracy, precision, recall, F1 e matriz de confusão).
- `backend/app/services/classification_service.py` carregando os pesos.
- Rotas `/api/v1/classification/*`.

**Critérios de aceite**

- [ ] Dataset real preparado com as classes `REGULAR` e `IRREGULAR`.
- [ ] Treino executado e pesos salvos.
- [ ] Métricas do relatório são resultado real do conjunto de teste.
- [ ] `GET /api/v1/classification/model-info` retorna versão e métricas reais.
- [ ] `POST /api/v1/classification/predict` classifica uma imagem enviada.
- [ ] Ocorrência criada sem modelo disponível continua sendo registrada (não bloqueia).
- [ ] Testes automatizados do serviço de classificação passando.

---

## FASE 4 — Simulador IoT

**Escopo:** sensores virtuais enviando telemetria real via HTTP.

**Entregáveis**

- `simulator/core/sensor.py` (sensor ultrassônico virtual com variação de ocupação).
- `simulator/sensors/runner.py` (loop de envio com intervalo configurável).
- Múltiplos sensores, cada um associado a um contêiner.
- Modo de simulação de nível crítico.

**Critérios de aceite**

- [ ] `python -m simulator.sensors.runner` envia leituras contínuas para a API.
- [ ] Cada leitura aparece em `GET /api/v1/containers/{code}/readings`.
- [ ] `alert_level` corresponde aos limiares 80/90.
- [ ] É possível forçar um sensor a nível crítico e ver o alerta `CRITICAL`.
- [ ] Toda leitura persistida tem `is_simulated = true`.

---

## FASE 5 — RPA Playwright

**Escopo:** automação preenchendo portal administrativo fictício.

**Entregáveis**

- `rpa/portal/` — portal fictício (HTML + servidor local simples).
- `rpa/bot/dispatcher.py` — consulta fila, preenche portal, captura protocolo, devolve resultado.
- `rpa/bot/selectors.py` — seletores centralizados.
- Screenshots e relatório em `rpa/screenshots/` e `rpa/reports/`.

**Critérios de aceite**

- [ ] `python -m playwright install chromium` executado.
- [ ] Portal fictício sobe e aceita submissão manual.
- [ ] Robô processa uma ocorrência `PENDING_DISPATCH` de ponta a ponta.
- [ ] Ocorrência passa para `DISPATCHED` com `dispatch_protocol` preenchido.
- [ ] Execução registrada em `rpa_executions` com duração e evidência.
- [ ] Segunda execução para a mesma ocorrência retorna `409`.
- [ ] Falha controlada (portal fora do ar) resulta em `FAILED` sem corromper o estado.

---

## FASE 6 — Agente conversacional

**Escopo:** agente baseado em intenções com ferramentas sobre dados reais.

**Entregáveis**

- `backend/app/services/agent/`: `intent_parser.py`, `tools.py`, `session.py`, `agent.py`.
- Rotas `/api/v1/agent/*`.
- Testes de intenção, de ferramenta e de resposta para intenção desconhecida.

**Critérios de aceite**

- [ ] Pergunta de status por protocolo retorna dados reais do banco.
- [ ] Pergunta sobre nível de contêiner retorna a última leitura persistida.
- [ ] Pergunta sobre indicadores retorna o resumo real.
- [ ] `criar_ocorrencia` cria registro real e devolve protocolo.
- [ ] Pergunta não reconhecida recebe orientação, sem invenção de dados.
- [ ] Contexto de sessão mantém a última ocorrência citada.
- [ ] Interações persistidas em `agent_interactions`.

---

## FASE 7 — Integração, testes e CI/CD

**Escopo:** consolidação da qualidade e automação de verificação.

**Entregáveis**

- `.github/workflows/ci.yml`: lint, testes de backend e build do frontend.
- Teste de integração ponta a ponta (criar → classificar → despachar → resolvido).
- Cobertura mínima documentada.

**Critérios de aceite**

- [ ] Workflow verde no GitHub Actions.
- [ ] Teste ponta a ponta passando com banco temporário.
- [ ] Nenhum segredo versionado.
- [ ] `ruff check` e `pytest` obrigatórios no CI.

---

## FASE 8 — Documentação e apresentação

**Escopo:** fechamento acadêmico.

**Entregáveis**

- Documentação final com instruções de execução de cada módulo.
- Relatório com arquitetura, resultados reais das métricas e evidências (screenshots do RPA,
  dashboard, chat).
- Roteiro de demonstração.
- Seção explícita de limitações.

**Critérios de aceite**

- [ ] Todos os módulos executáveis seguindo apenas a documentação.
- [ ] Métricas e evidências anexadas são reais.
- [ ] Limitações listadas sem omissão.

## Resumo de status

| Fase | Status | Exige testes |
|---|---|---|
| 0 | ✅ concluída | configuração de lint/pytest validada |
| 1 | ⏳ pendente | sim |
| 2 | ⏳ pendente | sim |
| 3 | ⏳ pendente | sim |
| 4 | ⏳ pendente | sim |
| 5 | ⏳ pendente | sim |
| 6 | ⏳ pendente | sim |
| 7 | ⏳ pendente | sim |
| 8 | ⏳ pendente | — |