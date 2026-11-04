# Cidade Limpa — Simulador de IoT (FASE 4)

Sensores ultrassônicos **virtuais** que representam contêineres urbanos e enviam
telemetria (ocupação + distância) via HTTP para o backend FastAPI.

## Pré-requisitos

- Backend em execução (`POST /api/v1/sensors/readings`).
- Contêineres cadastrados (o `seed` do backend cria `CONT-001` até `CONT-006`).

```powershell
# terminal 1 — backend (com seed)
cd backend
python -m app.db.seed
python -m uvicorn app.main:app --reload --port 8000
```

## Como executar

```powershell
# envia leituras a cada SENSOR_INTERVAL_SECONDS (padrão 10 s)
python -m simulator.sensors.runner

# uma única rodada (útil para testar)
python -m simulator.sensors.runner --once

# força todos os sensores em nível crítico (>= 90%)
python -m simulator.sensors.runner --once --critical

# intervalo personalizado (5 s)
python -m simulator.sensors.runner --interval 5
```

## O que cada sensor faz

1. Tem identificador único (`SENSOR-001` … `SENSOR-006`) e um contêiner associado.
2. Varia a ocupação por um **passeio aleatório limitado** (`step_max`).
3. Calcula a distância ultrassônica (inversa à ocupação: vazio → distância máxima).
4. Envia via `POST` o payload `{sensor_id, container_code, fill_level, distance_cm, measured_at}`.
5. O **backend** deriva o alerta pelos limiares (80% → HIGH, 90% → CRITICAL).

## Configuração (variáveis de ambiente)

| Variável | Padrão | Descrição |
|---|---|---|
| `API_BASE_URL` | `http://127.0.0.1:8000` | URL base do backend |
| `SENSOR_INTERVAL_SECONDS` | `10` | intervalo entre rodadas |
| `STEP_MAX` | `3.0` | variação máxima de ocupação por leitura |
| `CONTAINER_DEPTH_CM` | `100.0` | profundidade nominal (distância quando vazio) |
| `REQUEST_TIMEOUT_SECONDS` | `5.0` | timeout da requisição HTTP |

## Estrutura

```
simulator/
├── config.py          # Settings (pydantic-settings) e especificações dos sensores
├── core/sensor.py     # Sensor (ocupação, distância, payload)
└── sensors/runner.py  # loop de envio e CLI
```

## Testes

```powershell
python -m pytest simulator/tests
```

> Observação no Windows/PowerShell: os logs saem em `stderr`, e o PowerShell pode
> marcar a execução com código de saída 1 mesmo com sucesso. Isso é apenas o
> redirecionamento de `stderr` — o simulador envia as leituras normalmente.
