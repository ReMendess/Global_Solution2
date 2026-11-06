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
| keras | 3.13.2 |
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
| Backend | 1 | `cd backend; python -m uvicorn app.main:app --reload --port 8000` |
| Docs da API | 1 | abrir `http://127.0.0.1:8000/docs` |
| Seed de demonstração | 1 | `cd backend; python -m app.db.seed` |
| Frontend web | 2 | `cd frontend; npm run web` (abre em `http://localhost:8081`) |
| Frontend mobile | 2 | `cd frontend; npm start` (Expo Go, SDK 57) |
| Testes do frontend | 2 | `cd frontend; npm test` |
| Build web estático | 2 | `cd frontend; npm run build:web` (gera `frontend/dist`) |
| Treino do modelo | 3 | rode no Google Colab — ver `docs/ML_TRAINING_COLAB.md` |
| Avaliação do modelo | 3 | `python -m ml.src.evaluate` (pós-treino local) |
| Classificação | 3 | `GET/POST /api/v1/classification/*` (backend) |
| Simulador IoT | 4 | `python -m simulator.sensors.runner` (opções: `--once`, `--critical`, `--interval`) |
| Portal fictício | 5 | `python -m rpa.portal.server --port 8100` |
| Robô RPA | 5 | `python -m rpa.bot.dispatcher` (opções: `--max-demands`) |
| Agente | 6 | `POST /api/v1/agent/messages` (backend) |

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
| `CORS_ORIGINS` | `["*"]` | Origens liberadas (Expo web/mobile) |

## 7. Limitações conhecidas do ambiente

1. **OneDrive:** o repositório está dentro de uma pasta sincronizada, o que pode bloquear o arquivo
   SQLite durante a sincronização.
   **Status verificado na FASE 1:** o processo `OneDrive.exe` **não estava em execução**, portanto a
   sincronização estava parada durante o desenvolvimento e os testes.
   Se o cliente voltar a rodar, pausar com:
   `& "C:\Program Files\Microsoft OneDrive\OneDrive.exe" /pause`
   Para retomar: `& "C:\Program Files\Microsoft OneDrive\OneDrive.exe" /resume`
2. **TensorFlow apenas em CPU (treino no Google Colab):** o treino do MobileNetV2 **não será feito
   nesta máquina**. A FASE 3 entrega o notebook e o pipeline; o treinamento será executado no Google
   Colab (GPU) e os pesos/metadados voltam para `ml/models/`. O backend apenas carrega os pesos.
3. **Playwright não instalado:** o download do Chromium (~150 MB) será feito na Fase 5.
4. **Sem autenticação real:** o perfil é identificado pelo cabeçalho `X-User-Role`
   (`CITIZEN` por padrão, `ADMIN` para as rotas administrativas). Revisão prevista para a Fase 7.
5. **Sem Docker:** a entrega é executada diretamente no host; não há containerização prevista.
6. **Repositório git sem `remote` configurado:** o GitHub privado será conectado quando o usuário
   definir a URL. Os commits são locais.

## 8. Checklist de verificação da FASE 0 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Lint | `python -m ruff check .` | `All checks passed!` |
| Formatação | `python -m ruff format --check .` | `1 file already formatted` (sem diferenças) |
| Testes | `python -m pytest` | `42 passed in 0.11s` |
| Versionamento | `git log --oneline` | `9cfd7b8 chore: fase 0 - estrutura do repositorio e documentacao de planejamento` |
| Árvore de arquivos | `git status --porcelain` | vazio (nada pendente) |

## 9. Checklist de verificação da FASE 1 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Lint | `python -m ruff check .` | `All checks passed!` |
| Formatação | `python -m ruff format --check .` | `51 files already formatted` |
| Testes | `python -m pytest` | `89 passed` |
| Seed | `cd backend; python -m app.db.seed` | 2 usuários, 6 contêineres, 6 leituras, 6 ocorrências |
| API | `python -m uvicorn app.main:app --port 8000` | subiu em 127.0.0.1:8000 sem erro |
| Health | `GET /health` | `{"status":"ok","database":"ok","model_loaded":false}` |
| Registro | `POST /api/v1/occurrences` | `201`, protocolo `CL-2026-000007`, imagem gravada |
| Consulta | `GET /api/v1/occurrences/protocol/{protocol}` | `200` com os dados persistidos |
| Telemetria | `POST /api/v1/sensors/readings` (93,5%) | `201` com `alert_level: CRITICAL` |
| Perfil | `GET /api/v1/occurrences` sem cabeçalho | `403` (regra de acesso aplicada) |
| Dashboard | `GET /api/v1/dashboard/summary` | totais reais do banco (7 ocorrências) |
## 10. Checklist de verificação da FASE 2 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Instalação das dependências | `cd frontend; npm install` + `npx expo install ...` | 574 + 107 + 324 pacotes instalados |
| Versões do frontend | `package.json` | Expo SDK 57.0.31, React 19.2.3, RN 0.86.3, expo-router 57.0.29 |
| Tipos | `cd frontend; npm run typecheck` | sem erros |
| Testes | `cd frontend; npm test` | `46 passed` (6 suítes) |
| Build web | `npm run build:web` | `Web Bundled 21830ms` (808 módulos), `Exported: dist` |
| Servidor web | `npm run web` | `Waiting on http://localhost:8081` |
| Página inicial | `GET http://localhost:8081/` | `200`, 1.291 bytes (HTML do Expo Router) |
| Bundle | `GET /node_modules/expo-router/entry.bundle?...` | `200`, 4.165.308 bytes; contém `Cidade Limpa`, `Registrar ocorrência`, `dashboard/summary`, `X-User-Role` |
| CORS (preflight) | `OPTIONS /api/v1/meta/enums` com `Origin: http://localhost:8081` | `200`, `access-control-allow-origin: *` |
| Integração real | `GET /api/v1/dashboard/summary` com `X-User-Role: ADMIN` | `200` com 7 ocorrências do banco |
| Imagens | `GET /uploads/{arquivo}` | `200` com `image/png` (novo teste no backend) |
| Backend após a fase | `python -m pytest` | `91 passed` |

**Observação:** a verificação foi feita por HTTP (servidor Metro + backend). A interação visual
(clicar, preencher formulário) depende de um navegador/dispositivo e ficou registrada como
validação manual pendente no relatório da fase.
## 11. Checklist de verificação da FASE 3 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Lint / formato | `python -m ruff check .` + `ruff format --check .` | `All checks passed!` / sem diferenças |
| Testes backend | `python -m pytest` | `102 passed` (11 novos de classificação) |
| Dataset (sintético) | `discover` + `split_dataset` | divisão 70/15/15 com `manifest.json` gerado |
| Modelo | `build_model()` real | `MobileNetV2` → saída `(None, 2)`; cabeça com 2.562 parâmetros; ajuste fino libera 19 camadas |
| Rota sem pesos | `GET /api/v1/classification/model-info` | `503` |
| Rota com pesos (fixture) | `POST /api/v1/classification/predict` | `200` com `label`/`probabilities` |
| Integração | ocorrência com foto preenche `model_label`/`confidence` | validado por teste |
| Notebook | `cidade_limpa_mobilenetv2.ipynb` | 23 células, nbformat 4 |

**Pendências (fora do meu controle):** executar o treino no Colab e publicar os pesos em
`ml/models/`. Como a inferência ainda não tem pesos reais, `model_loaded` segue `false` e as
ocorrências seguem marcadas para revisão humana — comportamento correto e progressivo.
## 12. Checklist de verificação da FASE 4 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Lint / formato | `python -m ruff check .` + `ruff format --check .` | `All checks passed!` / sem diferenças |
| Testes | `python -m pytest` | `113 passed` (11 do simulador) |
| Envio normal | `python -m simulator.sensors.runner --once` | 6 leituras enviadas (NORMAL/HIGH/CRITICAL) |
| Envio crítico | `--once --critical` | 6 leituras em CRITICAL (90–100%) |
| Persistência | `GET /api/v1/containers/{code}/readings` | leituras presentes, com `distance_cm` e `alert_level` |
| Dashboard | `GET /api/v1/dashboard/containers` | contêineres críticos listados em `critical_codes` |
## 13. Checklist de verificação da FASE 5 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Playwright | `python -m playwright install chromium` | Chromium 1248 instalado |
| Lint / formato | `python -m ruff check .` + `ruff format --check .` | `All checks passed!` / sem diferenças |
| Testes | `python -m pytest` | `129 passed` (16 de RPA) |
| Portal | `python -m rpa.portal.server --port 8100` | GET formulário + POST com `PORTAL-XXXX` |
| E2E | robô processa a fila | ocorrência `PENDING_DISPATCH` → `DISPATCHED` (`PORTAL-0001`) |
| Duplicidade | 2ª `SUCCESS` | `409` (teste automatizado) |
## 14. Checklist de verificação da FASE 6 (executado)

| Item | Comando | Resultado real |
|---|---|---|
| Lint / formato | `python -m ruff check .` + `ruff format --check .` | `All checks passed!` / sem diferenças |
| Testes | `python -m pytest` | `147 passed` (18 do agente) |
| Criação pelo chat | `registrar ocorrência … em Perdizes` | `CL-2026-000010`, `OVERFLOW`, `HIGH` |
| Continuidade | `e o status?` | usou contexto → protocolo da última ocorrência |
| Contêiner | `nível do contêiner CONT-001` | `96,8%`, `CRITICAL` |
| Pontos de coleta | `quais são os pontos de coleta?` | 6 pontos |
| Indicadores | `quantas ocorrências existem?` | 10 (real do banco) |
| Desconhecida | `qual a previsão do tempo?` | orientação, sem invenção |
| Histórico | `GET /api/v1/agent/sessions/sess-demo` | 6 interações persistidas |