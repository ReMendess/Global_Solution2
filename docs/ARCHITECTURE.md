# Arquitetura do Smart Clean City


## 1. Princípio central

O **backend FastAPI é o núcleo**. Todo módulo (frontend, simulador, RPA, agente) conversa com
ele via **HTTP/JSON**. 

```
                        ┌────────────────────────────────────────────┐
                        │            FastAPI (núcleo)                │
   ┌──────────────┐     │  ┌──────────┐  ┌───────────┐  ┌──────────┐ │
   │  Frontend    │────▶│  │ Routers  │─▶│ Services  │─▶│  Models  │ │
   │ Expo / RN Web│◀────│  │ (REST)   │◀─│ (regras)  │◀─│ SQLAlchemy│ │
   └──────────────┘     │  └──────────┘  └───────────┘  └────┬─────┘ │
                        │        ▲             │              │       │
   ┌──────────────┐     │        │             ▼              ▼       │
   │  Simulador   │────▶│  ┌─────┴─────┐  ┌─────────┐   ┌───────────┐ │
   │  IoT (ESP32) │     │  │  Schemas  │  │ Serviço │   │  SQLite   │ │
   └──────────────┘     │  │ Pydantic  │  │   ML    │   │  (disco)  │ │
                        │  └───────────┘  └────┬────┘   └───────────┘ │
   ┌──────────────┐     │                      │                     │
   │  RPA (Playwright)│─│──────────────────────┘                     │
   └──────┬───────┘     └────────────────────────────────────────────┘
          │                                  ▲
          ▼                                  │
   ┌──────────────┐                  ┌───────┴──────┐
   │   Portal     │                  │   Agente     │
   │ administrativo│                 │ (intenções)  │
   │  fictício    │                  └──────────────┘
   └──────────────┘
```

## 2. Fluxo ponta a ponta (ocorrência)

```
[1] Cidadão envia foto + bairro + localização
      → Frontend: POST /api/v1/occurrences (multipart)
[2] Backend valida o payload com Pydantic
      → grava Occurrence (status OPEN) + OccurrenceImage
      → StatusHistory: OPEN
[3] Backend chama o serviço de classificação (MobileNetV2)
      → grava model_label, confidence, category, priority
      → StatusHistory: CLASSIFIED → PENDING_DISPATCH
      → devolve o protocolo ao cidadão (nunca bloqueia o registro)
[4] RPA lê GET /api/v1/rpa/queue (demandas elegíveis)
      → abre o portal administrativo fictício
      → preenche os dados da ocorrência e submete
      → captura o protocolo do portal
      → POST /api/v1/rpa/executions com sucesso/erro
[5] Backend atualiza a ocorrência para DISPATCHED
      → StatusHistory: DISPATCHED (com o número protocolado)
```
