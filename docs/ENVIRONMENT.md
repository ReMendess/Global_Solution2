# ENVIRONMENT.md — Ambiente verificado e setup

> Todas as versões abaixo foram **verificadas por execução** nesta máquina durante a FASE 0
> (Windows, PowerShell). Nada aqui é estimado.

## 1. Ambiente verificado

| Componente | Versão verificada | Comando de verificação |
|---|---|---|
| Sistema | Windows (win32) | — |
| Python | 3.13.5 | `python --version` |
| pip | 25.1.1 | `pip --version` |
| Git | 2.55.0.windows.5 | `git --version` |
| Node.js | 22.17.0 | `node --version` |
| npm | 10.9.2 | `npm --version` |
| npx | 10.9.2 | `npx --version` |
| SQLite (via `sqlite3`) | 3.49.1 | `python -c "import sqlite3;print(sqlite3.sqlite_version)"` |

## 2. Bibliotecas Python já instaladas e validadas

| Biblioteca | Versão |
|---|---|
| fastapi | 0.119.0 |
| uvicorn | 0.37.0 |
| pydantic | 2.14.1 |
| pydantic-settings | 2.14.1 |
| SQLAlchemy | 2.0.49 |
| python-multipart | 0.0.20 |
| requests | 2.32.5 |
| httpx | 0.28.1 |
| pytest | 9.1.1 |
| ruff | 0.14.0 |
| tensorflow | 2.20.0 |
| keras | 3.11.3 |
| scikit-learn | 1.8.0 |
| opencv-python | 4.12.0.88 |
| pillow | 11.3.0 |
| numpy | 2.2.6 |
| matplotlib | 3.10.6 |
| seaborn | 0.13.2 |

**Ainda não instalado (previsto por fase):**

| Biblioteca | Fase | Comando |
|---|---|---|
| `playwright` + Chromium | 5 | `python -m pip install playwright` e `python -m playwright install chromium` |

## 3. Setup do ambiente

```powershell
# Na raiz do repositório
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
Copy-Item .env.example .env
```

Observação: se o PowerShell bloquear o script de ativação, execute uma vez
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`.

## 4. Comandos de qualidade (disponíveis desde a FASE 0)

```powershell
python -m ruff check .            # lint
python -m ruff format .           # formatação (remove --check para aplicar)
python -m pytest                  # testes (testpaths = backend/tests)
```

## 5. Como executar cada módulo

| Módulo | Fase | Comando (a partir da raiz) |
|---|---|---|
| Backend | 1 | `cd backend; uvicorn app.main:app --reload --port 8000` |
| Docs da API | 1 | abrir `http://127.0.0.1:8000/docs` |
| Seed de demonstração | 1 | `python -m data.seed.seed` (definido na Fase 1) |
| Frontend web | 2 | `cd frontend; npx expo start --web` |
| Frontend mobile | 2 | `cd frontend; npx expo start` (Expo Go) |
| Treino do modelo | 3 | `python -m ml.src.train` (definido na Fase 3) |
| Avaliação do modelo | 3 | `python -m ml.src.evaluate` (definido na Fase 3) |
| Simulador IoT | 4 | `python -m simulator.sensors.runner` (definido na Fase 4) |
| Portal fictício | 5 | `python -m rpa.portal.server` (definido na Fase 5) |
| Robô RPA | 5 | `python -m rpa.bot.dispatcher` (definido na Fase 5) |
| Agente | 6 | via API (`POST /api/v1/agent/messages`) |

Portas reservadas: **8000** (API), **8100** (portal fictício), **8081** (Metro/Expo).

## 6. Configuração por variáveis de ambiente

Todas as variáveis estão documentadas em [`.env.example`](../.env.example). O arquivo `.env` real é
ignorado pelo git.

| Variável | Padrão | Uso |
|---|---|---|
| `APP_ENV` | `development` | Comportamento da aplicação |
| `DATABASE_URL` | `sqlite:///./data/cidade_limpa.db` | Conexão SQLAlchemy |
| `UPLOAD_DIR` | `./data/uploads` | Destino das fotos |
| `MAX_UPLOAD_MB` | `5` | Limite de upload |
| `MODEL_PATH` | `./ml/models/...keras` | Pesos do modelo |
| `CONFIDENCE_THRESHOLD` | `0.70` | Revisão humana |
| `API_BASE_URL` | `http://127.0.0.1:8000` | Simulador e RPA |
| `SENSOR_INTERVAL_SECONDS` | `10` | Intervalo de telemetria |
| `RPA_PORTAL_URL` | `http://127.0.0.1:8100` | Portal fictício |
| `RPA_HEADLESS` | `true` | Navegador sem interface |

## 7. Limitações conhecidas do ambiente

1. **OneDrive:** o repositório está dentro de uma pasta sincronizada. O SQLite pode sofrer bloqueio
   de arquivo durante a sincronização. Recomendação: pausar a sincronização ao rodar testes que
   recriam o banco, ou mover o `.db` para fora do OneDrive via `DATABASE_URL` absoluto.
2. **TensorFlow apenas em CPU:** treino do MobileNetV2 será lento; manter dataset pequeno e registrar
   o tempo real de treino na Fase 3.
3. **Playwright não instalado:** o download do Chromium (~150 MB) será feito na Fase 5.
4. **Sem autenticação real nesta fase:** o controle de perfil será demonstrativo na Fase 1 e revisado
   na Fase 7.
5. **Sem Docker:** a entrega é executada diretamente no host; não há containerização prevista.
6. **Repositório git sem `remote` configurado nesta fase:** o GitHub privado será conectado quando o
   usuário definir a URL. O commit inicial é local.

## 8. Checklist de verificação da FASE 0

| Item | Resultado |
|---|---|
| `python -m ruff check .` | executado no fechamento da fase |
| `python -m ruff format --check .` | executado no fechamento da fase |
| `python -m pytest` | executado no fechamento da fase |
| `git log --oneline` | commit inicial presente |