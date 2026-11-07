# FINAL_REPORT.md — Relatório final do projeto

> **Smart Clean City** — Plataforma Inteligente de Monitoramento e Gestão de Resíduos Urbanos.
> FIAP Global Solution 2026.2 · CitizenTech. Desenvolvimento individual com assistência do Cline.
>
> Este documento consolida arquitetura, resultados **reais** e limitações. Nenhuma métrica ou
> evidência é estimada.

## 1. Problema e solução

Identificar, registrar, monitorar e encaminhar ocorrências de descarte irregular e transbordamento
de contêineres é manual e sem rastreabilidade.

A solução entrega um ecossistema integrado: o **cidadão** registra a ocorrência com foto e bairro;
um **modelo de visão computacional** (MobileNetV2) classifica a imagem (`REGULAR`/`IRREGULAR`), com o
backend calculando categoria e prioridade; a demanda é encaminhada automaticamente por um **RPA
(Playwright)** a um portal administrativo demonstrativo; contêineres são monitorados por **sensores
simulados** (ESP32 virtual) e um **agente conversacional** responde com dados reais. Um **dashboard**
consolida os indicadores.

## 2. Arquitetura (resumo)

FastAPI é o núcleo; todo o restante consome exclusivamente a API REST, persistindo em SQLite.

```
cidadão → frontend (Expo/RN Web) ──┐
simulador IoT (ESP32 virtual) ─────┤
robô RPA (Playwright) ─────────────┼──► FastAPI (validação, regras, ML) ──► SQLite
agente (intenções + ferramentas) ──┘                 │
                                                    └──► portal administrativo fictício
```

Camadas do backend: `api/routes` (HTTP + validação) → `services` (regras de negócio) → `models`
(SQLAlchemy) → SQLite. O modelo de ML é carregado pelo serviço de classificação (lazy, com cache).

## 3. Resultados reais (verificados por execução)

### 3.1 Testes e qualidade

| Métrica | Valor real |
|---|---|
| Testes automatizados | **149 passing** (backend + simulador + RPA) |
| Cobertura (`backend/app` + `simulator` + `rpa`) | **88%** (2068 statements, 244 missed) |
| Lint (`ruff check`) | `All checks passed!` |
| Formatação (`ruff format --check`) | sem diferenças |
| Testes de frontend (Jest) | 46 passing |
| Typecheck (frontend) | sem erros |
| Build web (frontend) | `Web Bundled` (808 módulos) |

### 3.2 Modelo de visão computacional (MobileNetV2)

Modelo treinado no Google Colab (GPU), publicado em `ml/models/`:

| Métrica | Valor real |
|---|---|
| **Acurácia (conjunto de teste)** | **0,7273** (72,73%) |
| Precisão ponderada | 0,7336 |
| Recall ponderado | 0,7273 |
| F1 ponderado | 0,7242 |
| Matriz de confusão (33 imagens) | `[[10, 6], [3, 14]]` |
| Dataset | ~103–104 imagens/classe (treino 72/72, val 15/15, teste 16/17) |
| Arquitetura | MobileNetV2 (ImageNet) + transfer learning |

> A acurácia de 0,7273 é **resultado real** de um dataset pequeno. Está abaixo do "desejável"
> (0,75), algo esperado e explicitamente sinalizado — nenhuma métrica foi ajustada.

**Evidência:** `ml/models/cidade_limpa_mobilenetv2.keras`,
`ml/models/cidade_limpa_mobilenetv2.metadata.json`, `ml/reports/matriz_confusao.png`.

### 3.3 Verificações ponta a ponta por módulo

| Módulo | Resultado real |
|---|---|
| Backend | `uvicorn` sobe; `/health` → `model_loaded: true` |
| Registro de ocorrência | `POST /occurrences` grava, classifica (quando há foto) e devolve protocolo |
| RPA | robô processa a fila → ocorrência `DISPATCHED` com `PORTAL-0001` |
| Simulador | `--once --critical` envia 6 leituras, alerta correto (80/90) |
| Agente | responde status/nível/indicadores com dados reais; orienta intenção desconhecida |
| Dashboard | `summary` reflete o banco (10 ocorrências na última validação) |
## 4. Critérios gerais de aceite (PROJECT_CONTEXT §14)

- [x] Aplicação web executável (React Native Web)
- [x] Aplicação mobile executável (Expo Go, SDK 57 — compilada; não testada em aparelho físico)
- [x] Backend funcional
- [x] Persistência no banco (SQLite)
- [x] Classificação com modelo **efetivamente treinado** (accuracy 0,7273 real)
- [x] Simulador IoT enviando dados
- [x] RPA preenchendo portal demonstrativo
- [x] Agente consultando informações reais
- [x] Dashboard apresentando indicadores
- [x] Testes automatizados executados
- [x] Documentação atualizada
- [x] Limitações identificadas

## 5. Limitações (consolidadas, sem omissão)

1. **Acurácia do modelo (0,7273) abaixo do desejável:** dataset pequeno (~100/img/classe). O app
   sinaliza revisão humana via `needs_human_review`.
2. **App mobile não testado em aparelho físico:** fica no Expo Go (SDK 57); a rotina web foi
   validada, a rotina nativa depende do avaliador.
3. **Autenticação demonstrativa:** perfil por cabeçalho `X-User-Role` (forjável), sem JWT/senha.
4. **CI não rodou em runner real:** o repositório segue local (sem `remote`); o workflow está pronto
   e validado, mas só "fica verde" após o `push` ao GitHub privado.
5. **Imagens servidas em `/uploads` sem controle de acesso.**
6. **Contexto do agente em memória:** perdido ao reiniciar o processo.
7. **Parser do agente por palavras-chave:** vocabulário limitado; extração de bairro por regex.
8. **Simulador sem agendador preciso** e **sem fila de retry** (leituras de um ciclo são perdidas se
   o backend estiver fora).
9. **RPA sem screenshot** em execução headless (`screenshot_path` modelado, não capturado).
10. **Validação visual do frontend manual** (sem navegador headless na suíte).
11. **Ambiente sem Docker:** execução direta no host; TensorFlow em CPU no local.
12. **Artefatos de demo não versionados:** banco, uploads, pesos e relatórios são gerados localmente
    (`.gitignore`), como esperado.

## 6. Estrutura de evidências

| Evidência | Localização |
|---|---|
| Métricas do modelo | `ml/models/cidade_limpa_mobilenetv2.metadata.json` |
| Matriz de confusão | `ml/reports/matriz_confusao.png` |
| Relatório por fase | `docs/PHASE_1_REPORT.md` … `docs/PHASE_7_REPORT.md` |
| Roteiro de demonstração | `docs/DEMO_SCRIPT.md` |
| Guia de execução | `docs/EXECUTION_GUIDE.md` |
| Estratégia de testes | `docs/TESTING.md` |
| Decisões (ADRs) | `docs/DECISIONS.md` |
| Contrato REST | `docs/API_SPEC.md` |