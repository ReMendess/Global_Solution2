# TESTING.md — Estratégia de testes e comandos

> Documenta como os testes do Smart Clean City são organizados, executados e medidos.
> Resultado real na FASE 7: **149 testes, cobertura de 88%**.

## 1. Onde estão os testes

| Suite | Local | Foco |
|---|---|---|
| Backend | `backend/tests/` | FastAPI (TestClient), serviços, regras de negócio, RPA e agente |
| Simulador | `simulator/tests/` | sensor, runner (com sessão falsa) |
| RPA | `rpa/tests/` | funções puras do robô e portal fictício |
| Frontend | `frontend/src/**/*.test.ts(x)` | cliente HTTP, formatação, validação, componentes |

## 2. Camadas de teste

- **Unidade (`@pytest.mark.unit`):** regras puras — prioridade, limiares de alerta, dedup,
  interpretação de intenções, formatação/validação do frontend.
- **Integração (`@pytest.mark.integration`):** subimos a aplicação com `TestClient` e um banco
  SQLite temporário; cada teste valida o comportamento fim a fim de uma rota/serviço.
- **Ponta a ponta (`test_e2e_flow.py`):** o ciclo completo da ocorrência (registro → fila do RPA →
  despacho → resolução), com a trilha de auditoria verificada.

### Isolamento

O `backend/tests/conftest.py` cria um banco SQLite e um diretório de uploads temporários e aponta
`MODEL_PATH` para um arquivo inexistente. Assim a suíte é determinística, independente de existir ou
não um modelo real em `ml/models/`. Os testes de classificação publicam um modelo próprio via
fixture quando precisam do caminho real de inferência.

## 3. Como executar

```powershell
# backend completo (inclui simulador e rpa, pois testpaths agrega as três pastas)
python -m pytest

# apenas backend
python -m pytest backend/tests

# apenas uma suite
python -m pytest backend/tests/test_e2e_flow.py

# com cobertura (relatório textual)
python -m pytest --cov=backend/app --cov=simulator --cov=rpa --cov-report=term

# frontend
cd frontend; npm test -- --ci
```

## 4. Lint e formatação

```powershell
python -m ruff check .          # lint
python -m ruff format --check .  # formatação
```

Os notebooks (`ml/notebooks/`) e os artefatos (`ml/data`, `ml/models`, `frontend`) ficam fora do
escopo do Ruff (`pyproject.toml` → `extend-exclude`).

## 5. Cobertura (verificada na FASE 7)

```
TOTAL  2068 statements  244 missed  88%
```

Pontos de menor cobertura (esperados/aceitáveis):

- `backend/app/db/seed.py` — script de demonstração, exercitado manualmente (não via teste).
- `rpa/bot/dispatcher.py` (38%) e `simulator/sensors/runner.py` (51%) — orquestração de processos
  (launch do navegador/loop infinito), coberta indiretamente; a lógica pura está testada
  separadamente.
- Os núcleos de serviços/rotas ficam acima de 90%.

## 6. O que o CI acrescenta

O workflow `.github/workflows/ci.yml` executa, a cada push/PR:

1. backend: instalação das dependências, `ruff check`, `ruff format --check`, `pytest --cov`;
2. verificação de segredos (`git grep` por padrões como `AKIA…`, `ghp_…`, `BEGIN … PRIVATE KEY`);
3. frontend: `npm ci`, `typecheck`, `npm test -- --ci`, `build:web`.