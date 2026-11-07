# DEMO_SCRIPT.md — Roteiro de demonstração

> Roteiro sugerido para apresentar o Cidade Limpa em ~10–15 minutos. Cada passo mostra uma
> funcionalidade real, com o comando e o resultado esperado.

## Preparação

```powershell
cd backend; python -m app.db.seed
```

Subir, em terminais separados:

```powershell
# 1. backend
cd backend; python -m uvicorn app.main:app --reload --port 8000

# 2. frontend
cd frontend; npm run web          # http://localhost:8081

# 3. portal fictício (para a parte do RPA)
python -m rpa.portal.server --port 8100
```

## Passo 1 — Problema e arquitetura (1 min)

Explicar que o FastAPI é o núcleo e que frontend/simulador/RPA/agente só falam com ele por HTTP.

Abrir `http://127.0.0.1:8000/docs` e mostrar `/health` com `"model_loaded": true`.

## Passo 2 — Dashboard e indicadores (2 min)

No frontend, clicar em **"Entrar como admin"** e abrir **Administração → Dashboard**:

- mostrar os totais por status/categoria/prioridade, o tempo médio de resolução e os contêineres
  por nível de alerta (esses números vêm de `/api/v1/dashboard/*`).

## Passo 3 — Registro de ocorrência + IA (3 min)

Ainda no frontend, ir em **Registrar**: preencher bairro, escolher categoria e enviar uma **foto**
(galeria).

- o backend grava a ocorrência, o modelo MobileNetV2 classifica a imagem e devolve `model_label`
  + `confidence`;
- mostrar o card de resultado com o **protocolo** (`CL-2026-…`) e o status/prioridade.

Depois, em **Consultar**, informar esse protocolo e mostrar o histórico de status.

Opcionalmente, demonstrar a rota direta:

```powershell
curl.exe -F "image=@foto.png" http://127.0.0.1:8000/api/v1/classification/predict
```

## Passo 4 — Telemetria IoT (2 min)

Em outro terminal:

```powershell
python -m simulator.sensors.runner --once --critical
```

Voltar ao frontend → **Administração → Contêineres** e mostrar a ocupação em **CRITICAL** (≥ 90%),
com o histórico de leituras do contêiner.

## Passo 5 — RPA encaminhando a demanda (3 min)

1. Como admin, abrir uma ocorrência e movê-la para **"Aguardando envio"** (`PENDING_DISPATCH`).
2. Rodar o robô:

```powershell
python -m rpa.bot.dispatcher
```

3. Mostrar que a ocorrência foi para **`DISPATCHED`** com `dispatch_protocol` (ex.: `PORTAL-0001`),
   e o histórico em **Administração** exibe a transição feita pelo **RPA**.

## Passo 6 — Agente conversacional (2 min)

Sem interface própria nesta fase, demonstrar via `curl` (ou a tela do frontend, quando integrada):

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/agent/messages `
  -H "Content-Type: application/json" `
  -d '{\"session_id\":\"demo\",\"message\":\"status da ocorrência CL-2026-000010\"}'
```

Mostrar também `pontos de coleta` e `indicadores`, e a resposta de **orientação** para uma pergunta
fora do domínio ("qual a previsão do tempo?").

## Passo 7 — Qualidade (1 min)

Mostrar o resultado dos testes e da cobertura:

```powershell
python -m pytest            # 149 passed
python -m pytest --cov=backend/app --cov=simulator --cov=rpa   # 88%
```

E citar as limitações relevante (acurácia 0,7273 com dataset pequeno; autenticação demonstrativa;
CI aguardando o push ao GitHub privado — ver `FINAL_REPORT.md` §5).

## Fechamento

Encerrar com os critérios de aceite atendidos (`FINAL_REPORT.md` §4) e o mapa de evidências (§6).