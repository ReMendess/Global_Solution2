# PHASE_4_REPORT.md — Simulador IoT

> Relatório de fechamento da FASE 4. Números e resultados vêm de execução real.

## 1. Escopo executado

Sensores ultrassônicos virtuais que representam contêineres urbanos e enviam telemetria via HTTP
para `POST /api/v1/sensors/readings`, conforme `docs/PROJECT_CONTEXT.md` §9.

## 2. Arquivos criados

```
simulator/__init__.py
simulator/config.py          # Settings + SensorSpec + 6 sensores padrão
simulator/core/__init__.py
simulator/core/sensor.py     # Sensor (ocupação, distância, payload)
simulator/sensors/__init__.py
simulator/sensors/runner.py  # loop de envio + CLI
simulator/README.md
simulator/tests/test_sensor.py
simulator/tests/test_runner.py
```

**Modificados:** `pyproject.toml` (`testpaths` inclui `simulator/tests`),
`.env.example` (`STEP_MAX`, `CONTAINER_DEPTH_CM`, `REQUEST_TIMEOUT_SECONDS`),
`backend/tests/test_project_structure.py` (assert de `testpaths`),
`docs/{ROADMAP,ENVIRONMENT,README}.md`.

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| Modelo do sensor | passeio aleatório limitado (`step_max`), determinístico por `seed` (testável) |
| Distância | inversa à ocupação (vazio → profundidade nominal; cheio → 0 cm) |
| Timestamp | `measured_at` em UTC naive (convenção do projeto em `core/clock.py`) |
| Sensores padrão | `SENSOR-001`…`SENSOR-006`, alinhados aos contêineres do seed |
| Alerta | derivado **no backend** (limiares 80/90), o simulador só envia o valor |
| Robusteza | falha individual de um sensor não derruba as demais (log e continua) |
| Modo crítico | `--critical` mantém ocupação >= 90%, exercitando o alerta `CRITICAL` |
| Importação | `__init__` sem importação ansiosa para permitir `python -m` sem avisos |

## 4. Verificações reais

```
python -m pytest simulator/tests   → 11 passed
python -m pytest                   → 113 passed (backend + simulador)
python -m ruff check .             → All checks passed!
```

**Integração ponta a ponta** (backend em `127.0.0.1:8000` + simulador):

| Verificação | Resultado |
|---|---|
| `--once` | 6 leituras enviadas, alertas NORMAL/HIGH/CRITICAL coerentes com a ocupação |
| `--once --critical` | 6 leituras em CRITICAL (90.76–99.5%) |
| Leituras persistidas | `GET /api/v1/containers/CONT-001/readings` retorna histórico com `distance_cm` |
| Estado dos contêineres | `current_fill_level` e `alert_level` atualizados |
| Dashboard | `critical_codes` lista os 6 contêineres após o modo crítico |
| Simulação marcada | toda leitura tem `is_simulated = true` (regra de governança) |

## 5. Critérios de aceite — atendidos

- [x] `python -m simulator.sensors.runner` envia leituras contínuas
- [x] Leituras aparecem em `GET /api/v1/containers/{code}/readings`
- [x] `alert_level` deriva corretamente dos limiares 80/90
- [x] `--critical` produz alerta `CRITICAL` observável
- [x] `is_simulated = true` em toda leitura

## 6. Limitações identificadas

1. **Sem agendador próprio:** o intervalo é um `sleep` simples; não há agendamento preciso por
   sensor (todos enviam em lote a cada ciclo).
2. **Passeio aleatório sem semântica temporal:** a variação não modela sazonalidade ou picos reais,
   apenas um desvio limitado (adequado para demonstração).
3. **Logs em `stderr`:** no PowerShell o código de saída pode aparecer como `1` mesmo com sucesso
   (documentado no README do simulador).
4. **Sem autenticação na rota de sensores:** `POST /api/v1/sensors/readings` é aberta, assumindo
   rede local controlada (limitação já registrada na FASE 1).
5. **Sem reconexão automática:** se o backend ficar indisponível, as leituras daquele ciclo são
   perdidas (registradas apenas no log); não há fila de retry.

## 7. Próximo passo

**FASE 5 — RPA Playwright:** portal administrativo fictício + robô que consulta a fila de demandas e
preenche o portal, devolvendo o protocolo para a API.