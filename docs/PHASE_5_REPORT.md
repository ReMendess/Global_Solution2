# PHASE_5_REPORT.md — RPA Playwright

> Relatório de fechamento da FASE 5. Números e resultados vêm de execução real.

## 1. Escopo executado

Robô Playwright que consome a fila de demandas da API, preenche um portal administrativo
**fictício** e devolve o resultado (protocolo capturado) à API, conforme `docs/PROJECT_CONTEXT.md`
§10. Inclui o backend necessário (fila + registro de execuções) que ainda não existia.

## 2. Arquivos criados

```
backend/app/schemas/rpa.py
backend/app/services/rpa_service.py
backend/app/api/routes/rpa.py
backend/tests/test_rpa.py
rpa/__init__.py, rpa/config.py
rpa/portal/__init__.py, rpa/portal/server.py
rpa/bot/__init__.py, rpa/bot/dispatcher.py, rpa/bot/selectors.py
rpa/README.md
rpa/tests/test_dispatcher.py, rpa/tests/test_portal.py
```

**Modificados:** `backend/app/main.py`, `backend/app/api/routes/__init__.py`,
`backend/app/schemas/__init__.py`, `pyproject.toml` (`testpaths` + `rpa/tests`),
`backend/tests/test_project_structure.py`, `requirements.txt` (`playwright==1.64.1`),
`docs/{ROADMAP,API_SPEC,ENVIRONMENT,README}.md`.

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| Portal fictício | stdlib `http.server` (sem dependência), formulário HTML + protocolo sequencial `PORTAL-XXXX` |
| Seletores | centralizados em `rpa/bot/selectors.py` (robô e testes) |
| API do robô | `requests` (já listado) para fila/registro; Playwright apenas para o navegador |
| Testabilidade | funções puras (`build_form_data`, `parse_portal_protocol`) + `dispatch_one` com página fake |
| Duplicidade | backend rejeita segunda `SUCCESS` e só processa `PENDING_DISPATCH` |
| Falha | `FAILED` não muda o estado; `attempt` incrementa; robô continua as demais |
| Prioridade | fila ordenada por prioridade (CRITICAL primeiro), depois por criação |

## 4. Verificações reais

```
python -m pytest                  → 129 passed (16 novos de RPA)
python -m ruff check .            → All checks passed!
python -m playwright install chromium → Chromium 1248 instalado
```

**Integração ponta a ponta** (backend + portal + robô):

| Etapa | Resultado |
|---|---|
| Criação da ocorrência | `CL-2026-000009`, status `OPEN` |
| Admin envia para a fila | `PENDING_DISPATCH` |
| Robô processa | 1 demanda processada |
| Ocorrência final | `DISPATCHED`, `dispatch_protocol = PORTAL-0001` |
| Auditoria | `PENDING_DISPATCH → DISPATCHED` por `RPA` |
| Execução registrada | `rpa_executions`: 1 registro `SUCCESS`, `PORTAL-0001` |

## 5. Critérios de aceite — atendidos

- [x] `python -m playwright install chromium` executado
- [x] Portal fictício sobe e aceita submissão
- [x] Robô processa `PENDING_DISPATCH` de ponta a ponta
- [x] Ocorrência → `DISPATCHED` com `dispatch_protocol`
- [x] Execução registrada com duração e `SUCCESS`
- [x] Segunda `SUCCESS` → `409`
- [x] Falha controlada → `FAILED` sem corromper estado

## 6. Limitações identificadas

1. **Sem screenshots ao rodar headless:** o `screenshot_path` está modelado, mas o robô não tira
   screenshot (registrado como pendência opcional).
2. **Portal em memória:** protocolos e histórico somem ao derrubar o servidor (gerados por contador).
3. **Sem fila de retry própria:** o robô processa uma vez; falhas de rede interrompem a execução.
4. **Rota de fila/execuções aberta (`interno`):** como na telemetria, presume rede local controlada.
5. **`max_demands` / seleção:** o robô processa até o limite, sem trava de concorrência para
   execuções simultâneas (cenário de 1 robô é o esperado).

## 7. Próximo passo

**FASE 6 — Agente conversacional:** interpretação de intenções + ferramentas que consultam a API
(`consultar_ocorrencia`, `consultar_container`, `listar_pontos_coleta`, `criar_ocorrencia`,
`consultar_indicadores`), com contexto por sessão e sem LLM externo.