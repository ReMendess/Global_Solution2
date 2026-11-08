# EXECUTION_GUIDE.md — Como executar cada módulo

> Guia único e consolidado para rodar o Smart Clean City do zero. Pressupõe um terminal PowerShell no
> Windows (os comandos são análogos no Linux/macOS). Versões verificadas em `docs/ENVIRONMENT.md`.

## 0. Pré-requisitos

- Python 3.13 (verificado 3.13.5), Node.js 22 + npm (verificado 22.17/10.9).
- (Somente RPA) Chromium do Playwright: `python -m playwright install chromium` (feito na FASE 5).

## 1. Instalação

```powershell
# Python (backend + simulador + RPA + ML)
python -m venv .venv
.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt -r requirements-dev.txt

# Frontend
cd frontend
npm install
cd ..
```

## 2. Backend (núcleo)

```powershell
cd backend
python -m app.db.seed                       # dados de demonstração (idempotente)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> **Importante para testar no celular (Expo Go):** use `--host 0.0.0.0` para o backend aceitar
> conexões da rede local. Se o app mostrar "Não foi possível conectar à API", verifique também se o
> firewall do Windows libera a porta 8000. Em testes somente na própria máquina (web), `127.0.0.1`
> já basta.

- Documentação interativa: http://127.0.0.1:8000/docs
- Saúde: `GET http://127.0.0.1:8000/health` → `"model_loaded": true` (se o modelo estiver em
  `ml/models/`).

## 3. Frontend (web e mobile)

```powershell
cd frontend
npm run web          # React Native Web em http://localhost:8081
# ou
npm start            # Expo (QR Code para o Expo Go no celular)
```

O app descobre a URL da API automaticamente (`EXPO_PUBLIC_API_URL` → host do Metro → localhost).

## 4. Simulador IoT

```powershell
# com o backend rodando
python -m simulator.sensors.runner            # envia a cada 10 s
python -m simulator.sensors.runner --once     # uma rodada
python -m simulator.sensors.runner --critical # força nível crítico (>=90%)
```

## 5. RPA (portal + robô)

```powershell
# terminal A — portal administrativo fictício
python -m rpa.portal.server --port 8100

# terminal B — robô (consulta a fila e preenche o portal)
python -m rpa.bot.dispatcher
# ou limitado: python -m rpa.bot.dispatcher --max-demands 3
```

O robô só processa ocorrências em `PENDING_DISPATCH`; ao concluir, grava o protocolo do portal e
move a ocorrência para `DISPATCHED`.

## 6. Agente conversacional

Rodando com o backend, use `POST /api/v1/agent/messages`:

```json
{ "session_id": "sess-1", "message": "status da ocorrência CL-2026-000010" }
```

Exemplos de mensagens: `nível do contêiner CONT-001`, `pontos de coleta`, `indicadores`,
`registrar ocorrência de transbordamento em Pinheiros`.

## 7. Machine Learning

O treinamento roda no **Google Colab** (GPU) — roteiro em `docs/ML_TRAINING_COLAB.md`. O notebook é
`ml/notebooks/cidade_limpa_mobilenetv2.ipynb`.

Localmente (para reavaliar um modelo já treinado):

```powershell
python -m ml.src.evaluate --model-path ml/models/cidade_limpa_mobilenetv2.keras
```

## 8. Qualidade e testes

```powershell
python -m ruff check .           # lint
python -m ruff format --check .  # formatação
python -m pytest                 # 149 testes (backend + simulador + RPA)
python -m pytest --cov=backend/app --cov=simulator --cov=rpa  # cobertura (88%)
cd frontend && npm test -- --ci  # testes do frontend
```

## 9. Integração contínua

`.github/workflows/ci.yml` roda, no GitHub Actions, o lint + testes do backend (com cobertura),
a verificação de segredos e o build/teste do frontend. Requer o `push` do repositório (privado).

## 10. Portas e configuração

| Recurso | Porta | Variável principal |
|---|---|---|
| Backend (API) | 8000 | uvicorn `--host`/`--port` (padrão `--host 0.0.0.0`), `DATABASE_URL` |
| Frontend web | 8081 | `EXPO_PUBLIC_API_URL` |
| Portal fictício | 8100 | `RPA_PORTAL_URL` |

Variáveis e padrões completos: `.env.example` (`cp .env.example .env` para ajustar).