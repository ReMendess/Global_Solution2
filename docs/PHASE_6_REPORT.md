# PHASE_6_REPORT.md — Agente conversacional

> Relatório de fechamento da FASE 6. Números e resultados vêm de execução real.

## 1. Escopo executado

Agente baseado em **interpretação de intenções + ferramentas**, **sem LLM externo**, conforme
`docs/PROJECT_CONTEXT.md` §11. O agente lê apenas dados persistidos e, quando não há dado
suficiente, pede o que falta.

## 2. Arquivos criados

```
backend/app/schemas/agent.py
backend/app/services/agent/{__init__,intent_parser,tools,session,agent}.py
backend/app/api/routes/agent.py
backend/tests/test_agent_parser.py
backend/tests/test_agent.py
```

**Modificados:** `backend/app/main.py`, `backend/app/api/routes/__init__.py`,
`backend/app/schemas/__init__.py`, `docs/{ROADMAP,API_SPEC,ENVIRONMENT,README}.md`.

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| Interpretação | regras/palavras-chave + regex (sem modelo externo) |
| Ferramentas | reutilizam `occurrence_service`, `container_service` e `dashboard_service` |
| Contexto | em memória por `session_id` (última ocorrência e último contêiner) |
| Dados ausentes | o agente pede o dado que falta ou responde "não encontrado" (nunca inventa) |
| Persistência | toda mensagem vira uma `AgentInteraction` (auditoria) |
| Prioridade | intenção clara de ação (`registrar/denunciar`) vence consultas |

## 4. Verificações reais

```
python -m pytest                  → 147 passed (18 novos do agente)
python -m ruff check .            → All checks passed!
```

**Ponta a ponta (backend real + modelo publicado):**

| Mensagem | Resposta do agente |
|---|---|
| "registrar ocorrência de transbordamento em Perdizes" | `CL-2026-000010`, `OPEN`, `OVERFLOW`, `HIGH` |
| "e o status?" | usa contexto → `CL-2026-000010`, status `OPEN` |
| "nível do contêiner CONT-001" | `96,8%`, alerta `CRITICAL` (dado real) |
| "quais são os pontos de coleta?" | 6 pontos |
| "quantas ocorrências existem?" | 10 ocorrências (real) |
| "qual a previsão do tempo?" | orientação ("Não entendi…") |
| `GET /sessions/sess-demo` | 6 interações persistidas |

## 5. Critérios de aceite — atendidos

- [x] Status por protocolo → dados reais
- [x] Nível do contêiner → última leitura persistida
- [x] Indicadores → resumo real
- [x] `criar_ocorrencia` → registro real + protocolo
- [x] Mensagem desconhecida → orientação sem invenção
- [x] Contexto de sessão mantém última ocorrência
- [x] Interações persistidas em `agent_interactions`

## 6. Limitações identificadas

1. **Parser por palavras-chave:** vocabulário limitado; frases muito flexíveis podem cair na
   orientação. A cobertura é documentada nos testes.
2. **Extração de bairro por regex:** exige "em/no/na + Bairro" com inicial maiúscula; outras formas
   levam o agente a pedir o bairro.
3. **Contexto em memória:** perdido ao reiniciar o processo (limitação aceita para demonstração).
4. **`criar_ocorrencia` sem foto:** a ocorrência criada pelo chat fica sem imagem (e, sem modelo
   aplicado a ela, pode ficar em revisão humana).
5. **Sem autenticação:** as rotas do agente são públicas (sem dados pessoais além do texto da conversa).
6. **Descrição literal:** a descrição criada no chat é o texto bruto da mensagem (simples e honesto).

## 7. Próximo passo

**FASE 7 — Integração, testes e CI/CD:** teste ponta a ponta (ocorrência → classificação → despacho →
resolução), build do frontend no CI e GitHub Actions com lint + testes.