# Cidade Limpa

**Plataforma Inteligente de Monitoramento e Gestão de Resíduos Urbanos**

Projeto acadêmico da **FIAP Global Solution 2026.2 — CitizenTech** (desenvolvimento individual,
com assistência do Cline).

---

## 1. Problema

Identificar, registrar, monitorar e encaminhar ocorrências de descarte irregular de resíduos e de
transbordamento de contêineres urbanos é um processo manual, fragmentado e sem rastreabilidade.

O **Cidade Limpa** permite que o cidadão registre a ocorrência com foto e localização, que um modelo
de visão computacional classifique a imagem, que a demanda seja encaminhada automaticamente para um
portal administrativo (via RPA) e que o administrador acompanhe indicadores, contêineres e
execuções do sistema em um dashboard.

## 2. Escopo funcional

**Cidadão:** página inicial, registro de ocorrência com foto, bairro e localização, visualização da
classificação da IA, geração de protocolo, consulta de status e conversa com o assistente.

**Administrador:** dashboard de indicadores, consulta e filtro de ocorrências por categoria/status,
visualização de imagens e classificações, monitoramento de contêineres, histórico de sensores,
execuções do RPA e histórico do agente.

## 3. Tecnologias

| Camada | Stack |
|---|---|
| Frontend | React Native, Expo, Expo Router, React Native Web (responsivo desktop/mobile) |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy, SQLite, API REST |
| Machine Learning | TensorFlow/Keras, MobileNetV2 (transfer learning), OpenCV/Pillow, Scikit-learn |
| IoT | Python, ESP32 simulado, sensor ultrassônico virtual, HTTP/JSON |
| RPA | Python, Playwright, portal administrativo fictício |
| Agente | Python, interpretação de intenções, ferramentas que consultam a API (sem LLM externo) |
| Qualidade | Pytest, testes de frontend, GitHub Actions, GitHub privado |

## 4. Arquitetura em uma frase

O **FastAPI é o núcleo**: o frontend consome exclusivamente a API REST, o modelo MobileNetV2 é
carregado pelo serviço de classificação do backend, o simulador Python envia telemetria para os
endpoints de sensores, o RPA consome a fila de demandas e o agente consulta dados persistidos — tudo
sobre o mesmo SQLite.

Detalhes em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 5. Estrutura do repositório

```
Global_Solution2/
├── backend/
│   ├── app/                  # aplicação FastAPI
│   │   ├── api/routes/       # routers por domínio
│   │   ├── core/             # configuração, enums, regras transversais
│   │   ├── db/               # engine, sessão e inicialização do banco
│   │   ├── models/           # modelos SQLAlchemy
│   │   ├── schemas/          # schemas Pydantic (entrada/saída)
│   │   └── services/         # regras de negócio, ML, RPA, agente
│   └── tests/                # testes Pytest do backend
├── frontend/                 # app Expo / React Native Web (FASE 2)
├── ml/
│   ├── data/raw/             # dataset de entrada (não versionado)
│   ├── data/processed/       # dataset tratado (não versionado)
│   ├── notebooks/            # treino e avaliação
│   ├── src/                  # pipeline reutilizável
│   ├── models/               # pesos e metadados (não versionados)
│   └── reports/              # métricas, matriz de confusão (não versionado)
├── simulator/                # sensores virtuais de contêineres (FASE 4)
├── rpa/                      # robô Playwright + portal fictício (FASE 5)
├── data/                     # SQLite e uploads em runtime (não versionados)
└── docs/                     # documentação do projeto
```

## 6. Documentação

| Documento | Conteúdo |
|---|---|
| [`docs/PROJECT_CONTEXT.md`](docs/PROJECT_CONTEXT.md) | Documento-base do desafio (fonte da verdade) |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Componentes, fluxos e decisões de arquitetura |
| [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) | Entidades, colunas, enums e índices |
| [`docs/API_SPEC.md`](docs/API_SPEC.md) | Contrato REST planejado por fase |
| [`docs/BUSINESS_RULES.md`](docs/BUSINESS_RULES.md) | Enums canônicos, máquina de estados, prioridades, limiares |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Fases 0–8 com critérios de aceite verificáveis |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Registro de decisões (ADRs) |
| [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) | Ambiente verificado, setup e limitações |
## 7. Como preparar o ambiente

```bash
# 1. Clonar e entrar no repositório
git clone <url-do-repositorio-privado>
cd Global_Solution2

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate           # Windows (PowerShell)
# source .venv/bin/activate      # Linux/macOS

# 3. Instalar dependências
python -m pip install -r requirements.txt -r requirements-dev.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env           # Windows (PowerShell)
# cp .env.example .env           # Linux/macOS
```

A execução de cada módulo é detalhada em [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md).

## 8. Qualidade

```bash
python -m ruff check .           # lint
python -m ruff format --check .  # formatação
python -m pytest                 # testes
```

## 9. Status das fases

| Fase | Escopo | Status |
|---|---|---|
| 0 | Planejamento e estrutura | ✅ concluída |
| 1 | Backend, banco e dados simulados | ⏳ pendente |
| 2 | Frontend Expo e dashboard | ⏳ pendente |
| 3 | MobileNetV2 e visão computacional | ⏳ pendente |
| 4 | Simulador IoT | ⏳ pendente |
| 5 | RPA Playwright | ⏳ pendente |
| 6 | Agente conversacional | ⏳ pendente |
| 7 | Integração, testes e CI/CD | ⏳ pendente |
| 8 | Documentação e apresentação | ⏳ pendente |

Detalhamento e critérios de aceite em [`docs/ROADMAP.md`](docs/ROADMAP.md).

## 10. Dados simulados e integridade acadêmica

Todos os sensores, contêineres, imagens de exemplo e o portal administrativo são **simulados** e
identificados como tal no sistema. Métricas de treinamento somente serão publicadas quando
produzidas por execução real do modelo — nenhum resultado é inventado ou estimado.

## 11. Convenções de código

- Identificadores, enums e nomes de colunas em **inglês** (alinhados ao `PROJECT_CONTEXT.md`).
- Interface, documentação e mensagens ao usuário em **pt-BR**.
- Docstrings e comentários em pt-BR, curtos e objetivos.
- Nenhum código de fase futura antecipado; cada fase entrega apenas seu escopo.

## 12. Licença

Projeto acadêmico, sem licença de uso comercial.