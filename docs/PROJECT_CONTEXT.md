# PROJECT_CONTEXT.md — Global Solution.2

## 1. Identificação

**Projeto:** Cidade Limpa — Plataforma Inteligente de Monitoramento e Gestão de Resíduos Urbanos.

**Desafio:** FIAP Global Solution 2026.2 — CitizenTech.

**Desenvolvimento:** Individual, com assistência do Cline.

**Objetivo:** Construir um MVP funcional que integre aplicação web/mobile, inteligência artificial, visão computacional, automação RPA, IoT simulado e agente conversacional.

## 2. Problema

Dificuldade de identificar, registrar, monitorar e encaminhar ocorrências relacionadas ao descarte irregular de resíduos e transbordamento de contêineres urbanos.

A solução permitirá que cidadãos registrem problemas, que imagens sejam classificadas por um modelo de Machine Learning e que demandas sejam encaminhadas automaticamente para um portal administrativo demonstrativo.

Também haverá monitoramento de contêineres por sensores simulados e um assistente conversacional para consulta de informações.

## 3. Tecnologias obrigatórias

### Frontend
- React Native.
- Expo.
- Expo Router.
- React Native Web.
- Interface responsiva para desktop e mobile.

### Backend
- Python.
- FastAPI.
- Pydantic.
- SQLAlchemy.
- SQLite.
- API REST.

### Machine Learning
- TensorFlow/Keras.
- MobileNetV2.
- Transfer Learning.
- OpenCV/Pillow.
- Scikit-learn para avaliação.

### IoT
- Python.
- Simulação de ESP32.
- Sensor ultrassônico virtual.
- Comunicação HTTP/JSON.

### RPA
- Python.
- Playwright.
- Portal administrativo fictício.

### Agente
- Python.
- Interpretador de intenções.
- Regras de negócio.
- Ferramentas que consultam a API.
- Contexto simples por sessão.
- Sem necessidade de LLM externo.

### Qualidade e entrega
- Pytest.
- Testes de frontend.
- GitHub Actions.
- GitHub privado.
- Documentação Markdown.

## 4. Arquitetura

O FastAPI será o núcleo da solução.

O frontend consumirá exclusivamente a API REST.

O modelo MobileNetV2 será carregado pelo serviço de classificação do backend.

O simulador Python enviará telemetria para endpoints de sensores.

O RPA consultará a fila de demandas e utilizará Playwright para preencher um portal administrativo fictício.

O agente utilizará ferramentas controladas para consultar ocorrências, contêineres e indicadores.

O SQLite será utilizado para persistência de todos os módulos.

## 5. Funcionalidades

### Cidadão
- Visualizar página inicial.
- Registrar ocorrência.
- Enviar fotografia.
- Informar bairro e localização.
- Visualizar classificação da IA.
- Receber protocolo.
- Consultar status.
- Conversar com assistente.

### Administrador
- Dashboard de indicadores.
- Consultar ocorrências.
- Filtrar por categoria e status.
- Visualizar imagens.
- Consultar classificação.
- Monitorar contêineres.
- Consultar histórico de sensores.
- Consultar execuções do RPA.
- Consultar histórico do agente.

## 6. Regras de negócio

Categorias:
- ILLEGAL_DUMPING
- OVERFLOW
- DAMAGED_CONTAINER
- OTHER

Classes do modelo:
- REGULAR
- IRREGULAR

Status:
- OPEN
- CLASSIFIED
- PENDING_DISPATCH
- DISPATCHED
- IN_PROGRESS
- RESOLVED
- REJECTED

Prioridades:
- LOW
- MEDIUM
- HIGH
- CRITICAL

Alertas de ocupação:
- Menor que 80%: NORMAL.
- De 80% a 89%: HIGH.
- 90% ou mais: CRITICAL.

O modelo não poderá impedir o registro de uma ocorrência.
Classificações com baixa confiança deverão permitir revisão humana.
O encaminhamento via RPA deverá possuir controle contra duplicidade.
Dados simulados deverão ser identificados.

## 7. Entidades

- User
- Occurrence
- OccurrenceImage
- Container
- SensorReading
- RPAExecution
- AgentInteraction
- StatusHistory

Utilizar SQLAlchemy para persistência e Pydantic para validação das entradas e saídas da API.

## 8. Modelo de Machine Learning

Utilizar MobileNetV2 com transfer learning.

Pipeline:
1. Preparar dataset.
2. Identificar e validar classes.
3. Separar treinamento, validação e teste.
4. Redimensionar imagens.
5. Aplicar data augmentation.
6. Treinar o modelo.
7. Avaliar métricas.
8. Salvar pesos e metadados.
9. Carregar modelo na API.
10. Realizar inferência sobre imagens enviadas.

Registrar accuracy, precision, recall, F1-score e matriz de confusão.

Não inventar resultados de treinamento.

## 9. Simulador IoT

Criar múltiplos sensores virtuais representando contêineres urbanos.

Cada sensor deverá:
- Possuir identificador único.
- Estar associado a um contêiner.
- Gerar variações de ocupação.
- Enviar leituras via HTTP.
- Registrar data e hora.
- Permitir simular níveis críticos.

## 10. RPA

Criar um portal administrativo fictício.

O Playwright deverá:
1. Consultar demandas elegíveis.
2. Acessar o portal.
3. Preencher os dados da ocorrência.
4. Submeter a solicitação.
5. Capturar o protocolo.
6. Atualizar a ocorrência via API.
7. Registrar sucesso ou erro.

## 11. Agente conversacional

Criar um agente baseado em interpretação de intenções e ferramentas.

Ferramentas:
- consultar_ocorrencia
- consultar_container
- listar_pontos_coleta
- criar_ocorrencia
- consultar_indicadores

O agente deverá consultar dados efetivamente persistidos e não inventar informações.

Perguntas não reconhecidas deverão receber uma resposta de orientação.

## 12. Segurança e governança

- Validar entradas da API.
- Controlar acesso aos perfis.
- Não armazenar informações pessoais desnecessárias.
- Evitar exposição de imagens identificáveis.
- Identificar dados simulados.
- Registrar execuções do RPA.
- Registrar resultados do modelo e sua versão.
- Evitar duplicidade de ocorrências.
- Não expor credenciais no código.
- Implementar tratamento de exceções.

## 13. Fases de implementação

FASE 0 — Planejamento e estrutura.

FASE 1 — Backend, banco e dados simulados.

FASE 2 — Frontend Expo e dashboard.

FASE 3 — MobileNetV2 e visão computacional.

FASE 4 — Simulador IoT.

FASE 5 — RPA Playwright.

FASE 6 — Agente conversacional.

FASE 7 — Integração, testes e CI/CD.

FASE 8 — Documentação e apresentação.

## 14. Critérios gerais de aceite

- Aplicação web executável.
- Aplicação mobile executável.
- Backend funcional.
- Persistência no banco.
- Classificação utilizando modelo efetivamente treinado.
- Simulador IoT enviando dados.
- RPA preenchendo portal demonstrativo.
- Agente consultando informações reais do sistema.
- Dashboard apresentando indicadores.
- Testes automatizados executados.
- Documentação atualizada.
- Limitações identificadas.

## 15. Diretrizes para o Cline

Antes de qualquer implementação:
1. Ler este documento.
2. Analisar a estrutura existente.
3. Identificar o escopo da fase solicitada.
4. Verificar dependências e compatibilidade.
5. Apresentar um plano curto de execução.

Durante a implementação:
- Não antecipar funcionalidades de fases futuras.
- Não recriar componentes existentes.
- Não utilizar mocks para substituir funcionalidades que precisam ser reais.
- Não adicionar tecnologias sem justificativa.
- Manter arquitetura simples.
- Reutilizar componentes.
- Criar testes.
- Atualizar documentação.

Após cada fase:
1. Listar arquivos criados e modificados.
2. Explicar decisões técnicas.
3. Executar testes.
4. Apresentar resultados reais.
5. Identificar limitações.
6. Atualizar documentação.
7. Informar se os critérios de aceite foram atendidos.

**Regra fundamental:** nenhuma funcionalidade poderá ser considerada concluída apenas porque seu código foi gerado. Ela deverá ser executada e testada.