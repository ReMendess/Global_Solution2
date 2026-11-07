# PHASE_7_REPORT.md — Integração, testes e CI/CD

> Relatório de fechamento da FASE 7. Números e resultados vêm de execução real local; o único item
> que depende de infraestrutura externa (GitHub Actions) é explicitamente sinalizado.

## 1. Escopo executado

Teste de integração ponta a ponta, pipeline de CI no GitHub Actions, medição real de cobertura e
verificação de ausência de segredos.

## 2. Arquivos criados / modificados

```
.github/workflows/ci.yml           (novo)
backend/tests/test_e2e_flow.py     (novo, 2 testes ponta a ponta)
docs/TESTING.md                    (novo)
docs/PHASE_7_REPORT.md             (novo)
requirements-dev.txt               (+ pytest-cov==7.1.0)
docs/{ROADMAP,ENVIRONMENT,README}.md
```

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| e2e | dois testes: fluxo base (sem ML) e fluxo completo (com modelo de fixture) |
| CI | dois jobs paralelos (backend e frontend), mais um passo de verificação de segredos |
| Cobertura | `pytest-cov`, fonte `backend/app` + `simulator` + `rpa` |
| Segredos | `git grep` por padrões comuns (excluindo arquivos de teste, que citam os padrões) |
| Playwright no CI | não é necessário baixar o Chromium (os testes do RPA usam page fake + portal stdlib) |

## 4. Verificações reais

```
python -m pytest                          → 149 passed
python -m pytest --cov=...                → 88% (2068 statements, 244 missed)
python -m ruff check .                    → All checks passed!
python -m ruff format --check .           → 96 files formatted
git grep (segredos, fora de testes)       → nenhum resultado
yaml.safe_load(.github/workflows/ci.yml)  → válido
```

**Teste ponta a ponta (sem ML):** registro → `PENDING_DISPATCH` → `DISPATCHED` (`PORTAL-E2E-1`) →
`IN_PROGRESS` → `RESOLVED`, com trilha de 5 transições e 1 execução `SUCCESS` registrada.

**Teste ponta a ponta (com ML):** registro com foto → `CLASSIFIED` + `model_label` +
`PENDING_DISPATCH` → despacho → resolução, trilha de 6 transições.

## 5. Critérios de aceite — situação

- [x] Teste ponta a ponta passando com banco temporário
- [x] Nenhum segredo versionado
- [x] `ruff check` e `pytest` obrigatórios no CI (e verdes localmente)
- [x] Cobertura documentada (88%)
- [ ] Workflow verde no GitHub Actions — **pendente do `push`** (não há `remote` configurado)

## 6. Limitações identificadas

1. **CI não executado em runner real:** o repositório ainda não tem `remote` (GitHub privado). O
   `ci.yml` foi validado por parse YAML e espelha exatamente os comandos que passam localmente.
2. **TensorFlow no CI:** a instalação de `tensorflow` no Linux é pesada (~600 MB); o job de backend
   pode ser lento. Alternativa futura: usar `tensorflow-cpu` no CI.
3. **Cobertura não cobre CLI/scripts** (`seed`, `runner`, `run_bot`): intencionalmente, são
   orquestrações exercitadas manualmente; a lógica pura associada está testada.
4. **`coverage.xml`:** gerado para integrações futuras (ex.: Codecov), mas hoje só vira artefato.

## 7. Próximo passo

**FASE 8 — Documentação e apresentação:** fechar o README com instruções de execução de cada módulo,
consolidar evidências reais (métricas, matriz de confusão, execuções) e listar as limitações finais.