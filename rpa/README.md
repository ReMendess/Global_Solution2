# Cidade Limpa — RPA (FASE 5)

Robô **Playwright** que consulta a fila de demandas da API, preenche um **portal
administrativo fictício** e devolve o resultado (protocolo capturado) à API.

## Componentes

| Arquivo | Papel |
|---|---|
| `rpa/portal/server.py` | Portal administrativo fictício (HTTP local, stdlib) |
| `rpa/bot/selectors.py` | Seletores CSS do formulário |
| `rpa/bot/dispatcher.py` | Robô: fila → preenchimento → captura de protocolo → registro |
| `rpa/config.py` | Configuração (`.env`) |

## Pré-requisitos

1. Backend em execução com ocorrências em `PENDING_DISPATCH`.
2. Playwright instalado:

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

## Como executar

```powershell
# terminal 1 — backend (com seed)
cd backend
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000

# terminal 2 — portal administrativo fictício
python -m rpa.portal.server --port 8100

# terminal 3 — robô (processa a fila)
python -m rpa.bot.dispatcher
# ou com um número máximo de demandas
python -m rpa.bot.dispatcher --max-demands 3
```

## Fluxo do robô

1. `GET /api/v1/rpa/queue` → demandas em `PENDING_DISPATCH` (ordenadas por prioridade).
2. Abre o portal (Playwright, headless por padrão).
3. Preenche protocolo, categoria, prioridade, bairro, endereço e descrição.
4. Submete o formulário e captura o `PORTAL-XXXX`.
5. `POST /api/v1/rpa/executions` com `SUCCESS` (ou `FAILED` com a mensagem).
6. No backend, um `SUCCESS` move a ocorrência para `DISPATCHED` e grava `dispatch_protocol`.

## Controle contra duplicidade

- A fila só devolve ocorrências em `PENDING_DISPATCH`.
- Uma ocorrência só aceita **uma** execução `SUCCESS` (a segunda → `409`).
- `FAILED` não altera o status e pode ser reprocessada.

## Testes

```powershell
python -m pytest rpa/tests
```

Cobrem as funções puras do robô (mapeamento de formulário, extração de protocolo,
preenchimento com página fake) e o portal (formulário, submissão e protocolos sequenciais).