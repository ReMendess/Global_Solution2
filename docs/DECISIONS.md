# DECISIONS.md — Registro de decisões (ADRs)

> Formato leve: contexto → decisão → consequência. Decisões podem ser revisadas nas fases em que o
> tema for implementado, e a revisão deve ser registrada aqui.

## ADR-001 — Monorepo por domínio

**Contexto:** o projeto tem cinco módulos executáveis distintos (backend, frontend, ML, simulador,
RPA) que precisam ser entregues juntos.

**Decisão:** um único repositório com uma pasta por domínio na raiz.

**Consequência:** um clone e uma avaliação. Cada módulo tem seu próprio comando de execução; não há
pacote Python instalável nem workspace Node único nesta fase.

## ADR-002 — FastAPI como núcleo único

**Contexto:** o `PROJECT_CONTEXT.md` define o backend como núcleo e o frontend como consumidor
exclusivo da API REST.

**Decisão:** nenhum módulo acessa o SQLite diretamente. Simulador, RPA e agente usam HTTP ou as
funções de serviço internas.

**Consequência:** um único ponto de validação e auditoria. Custo: chamadas HTTP extras do simulador e
do RPA.

## ADR-003 — SQLite com `create_all()`, sem Alembic

**Contexto:** MVP acadêmico, um único desenvolvedor, schema definido na Fase 1.

**Decisão:** `Base.metadata.create_all(engine)` no startup e no seed. Alembic não é usado.

**Consequência:** simplicidade alta; alterações de schema exigem recriar `data/cidade_limpa.db`.
Se o schema mudar muito na Fase 7, reavaliar.

## ADR-004 — Enums como `VARCHAR` no banco

**Contexto:** o conjunto de status/categorias pode evoluir durante o projeto.

**Decisão:** persistir os valores como texto e validar com `Enum` do Python/Pydantic na aplicação.

**Consequência:** evita migração destrutiva no SQLite; exige validação consistente na camada de
schema.

## ADR-005 — Upload de imagem em disco

**Contexto:** SQLite não é adequado para BLOBs grandes e o repositório não deve guardar imagens.

**Decisão:** gravar arquivos em `UPLOAD_DIR` com nome gerado pelo servidor e persistir o caminho
relativo.

**Consequência:** `data/uploads/` fica fora do git; backup é responsabilidade do ambiente.

## ADR-006 — TensorFlow 2.20 + Keras 3 no Python 3.13

**Contexto:** o ambiente verificado já possui TensorFlow 2.20.0 e Keras 3.11.3 funcionando em Python
3.13.5 (CPU).

**Decisão:** usar essa combinação, fixada em `requirements.txt`, em vez de recriar um ambiente com
versões mais antigas.

**Consequência:** treino apenas em CPU (lento) → dataset pequeno e `IMAGE_SIZE` de 224×224 conforme o
MobileNetV2. Documentar o tempo real de treino na Fase 3.

## ADR-007 — Limiar de confiança configurável

**Contexto:** classificação com baixa confiança deve permitir revisão humana.

**Decisão:** `CONFIDENCE_THRESHOLD` em `.env`, padrão `0.70`; abaixo dele a ocorrência recebe
`needs_human_review = true`, mas é registrada normalmente.

**Consequência:** a decisão de revisão é auditável e ajustável sem alterar código.

## ADR-008 — O modelo nunca bloqueia o registro

**Contexto:** regra explícita do `PROJECT_CONTEXT.md` §6.

**Decisão:** falha de inferência é tratada como evento tolerável: `category = OTHER`,
`needs_human_review = true`, status segue para `PENDING_DISPATCH` (ou fica em revisão, conforme
decisão da Fase 1).

**Consequência:** a disponibilidade do registro independe do modelo; a classificação é um
enriquecimento.

## ADR-009 — Portal administrativo fictício local

**Contexto:** o RPA precisa de um alvo real sem depender de sistema externo ou credenciais.

**Decisão:** servir um portal HTML simples em `127.0.0.1:8100` a partir de `rpa/portal/`, com
formulário e página de confirmação contendo o protocolo.

**Consequência:** demonstração reproduzível offline; nenhuma credencial real é usada.

## ADR-010 — Agente sem LLM externo

**Contexto:** exigência explícita do desafio.

**Decisão:** interpretação por palavras-chave/expressões regulares + regras, com ferramentas que
consultam os serviços do backend e contexto por `session_id`.

**Consequência:** comportamento determinístico e testável; limitação de vocabulário precisa ser
documentada e respondida com mensagem de orientação.

## ADR-011 — Frontend criado a partir da Fase 2

**Contexto:** versões do Expo mudam com frequência e a Fase 0 não deve fixar dependências prematuras.

**Decisão:** `frontend/` permanece vazio nesta fase (`create-expo-app` na Fase 2).

**Consequência:** evita retrabalho de upgrade; a estrutura já está reservada no repositório.

## ADR-012 — Documentação em pt-BR, código em inglês

**Contexto:** o documento-base, o público e a avaliação são em português; o desafio usa enums em
inglês.

**Decisão:** textos, mensagens e docstrings em pt-BR; identificadores, tabelas, colunas e enums em
inglês.

**Consequência:** consistência com o `PROJECT_CONTEXT.md` e legibilidade para o avaliador.
## ADR-013 — Treino do modelo no Google Colab

**Contexto:** o treino do MobileNetV2 em CPU, nesta máquina (Windows + Python 3.13), levaria horas
para um número de épocas útil. O TensorFlow está instalado localmente, mas não há GPU disponível.

**Decisão:** na FASE 3 será entregue o notebook e o pipeline em `ml/src/`; o **treinamento será
executado pelo autor no Google Colab** (GPU gratuita) e os artefatos (pesos `.keras` + metadados JSON
com métricas reais) serão baixados para `ml/models/` e `ml/reports/`.

**Consequência:** o backend continua independente do ambiente de treino — apenas carrega os pesos.
O notebook precisa ser autocontido (instalar dependências, baixar dataset, treinar, avaliar, salvar).
Nenhuma métrica é publicada sem execução real.

## ADR-014 — Perfil de acesso por cabeçalho na FASE 1

**Contexto:** o desafio exige controle de acesso por perfil, mas não exige autenticação completa, e a
FASE 6 (agente) e a FASE 2 (frontend) precisam de rotas administrativas funcionais.

**Decisão:** identificar o perfil pelo cabeçalho `X-User-Role` (`CITIZEN` por padrão, `ADMIN` quando
informado). Rotas administrativas respondem `403` sem o perfil correto.

**Consequência:** sem JWT/senha nesta fase; a troca por autenticação real fica registrada para a
FASE 7 e está concentrada em `backend/app/api/deps.py`.

## ADR-015 — Flag `is_simulated` também em ocorrências

**Contexto:** as ocorrências criadas pelo seed são dados de demonstração e a regra de governança
exige identificar dados simulados (PROJECT_CONTEXT.md §12), mas `occurrences` não previa essa coluna
no desenho inicial.

**Decisão:** adicionar `is_simulated` (default `False`) em `occurrences`. Registros criados pela API
ficam `False`; o seed marca `True`.

**Consequência:** o dashboard e o agente podem distinguir demonstração de uso real. Pequena extensão
em relação ao `DATA_MODEL.md` original, registrada aqui e no próprio documento de modelo.
## ADR-016 — Expo SDK 57 (compatibilidade com Expo Go)

**Contexto:** o CLI do Expo oferece SDK 58 como "Latest" e SDK 57 como a versão suportada pelo
**Expo Go** disponível nas lojas. Um critério de aceite da FASE 2 é executar o app no Expo Go.

**Decisão:** fixar o projeto em **SDK 57** (`expo ~57.0.31`, React 19.2.3, RN 0.86.3, expo-router
57.0.29), criado com `create-expo-app --template expo-template-blank-typescript@sdk-57`.

**Consequência:** o app roda no Expo Go sem build nativo. Ao atualizar de SDK no futuro, validar
antes o suporte do Expo Go.

## ADR-017 — Template enxuto, sem demo de UI

**Contexto:** o template `default` do SDK 57 inclui `@expo/ui`, glass effects, splash animado e
componentes de demonstração que não fazem parte do escopo.

**Decisão:** usar `blank-typescript` e construir apenas os componentes necessários
(`screen`, `card`, `badge`, `button`, `text-field`, `choice-chips`, `states`).

**Consequência:** menos dependências nativas, bundle menor e código próprio integralmente
compreendido e testável.

## ADR-018 — Imagens servidas por `/uploads`

**Contexto:** o backend grava as fotos em `data/uploads` (ADR-005) e devolve apenas o caminho
relativo. O desafio exige que o administrador **visualize as imagens**.

**Decisão:** montar `StaticFiles` em `/uploads` no FastAPI apontando para `UPLOAD_DIR` — sem rota por
ocorrência e sem expor caminho absoluto do servidor.

**Consequência:** o frontend monta a URL com `buildUploadUrl(file_path)`. Em produção seria
necessário controle de acesso a essas imagens (registrado como limitação).

## ADR-019 — Perfil demonstrativo no cliente

**Contexto:** as rotas administrativas exigem `X-User-Role: ADMIN` (ADR-014), mas não há login.

**Decisão:** manter o perfil em um contexto React (`ProfileProvider`) com botão de alternância,
enviando o cabeçalho em todas as chamadas administrativas.

**Consequência:** a troca de perfil é imediata e explícita na interface; a substituição por
autenticação real (FASE 7) fica concentrada no `api-client` e no contexto de perfil.

## ADR-020 — URL da API resolvida em runtime

**Contexto:** a mesma aplicação roda na web (localhost), no Expo Go (IP da rede local) e no emulador.

**Decisão:** `resolveApiBaseUrl()` usa `EXPO_PUBLIC_API_URL` quando definido, senão o host do Metro
(`Constants.expoConfig.hostUri`) com a porta 8000, e por último `http://127.0.0.1:8000`.

**Consequência:** não é necessário editar código para trocar de ambiente, e o comportamento fica
coberto por testes unitários.
## ADR-021 — Notebook autocontido + normalização dentro do modelo

**Contexto:** o treino roda no Google Colab (ADR-013), onde o repositório privado não é acessível.
Além disso, o backend precisa fazer inferência com os **mesmos** pixels que o treino, sem repetir
a normalização.

**Decisão:** (1) o notebook `ml/notebooks/cidade_limpa_mobilenetv2.ipynb` replica o pipeline de
`ml/src/` de forma autocontida (mesmos hiperparâmetros e mesma ordem de classes); (2) a
normalização para [-1, 1] (`Rescaling`) é uma **camada interna do modelo salvo**, então o backend
envia pixels crus em [0, 255].

**Consequência:** o autor treina sem clonar o repositório; e o serviço de classificação não precisa
conhecer detalhes de pré-processamento do MobileNetV2 — basta redimensionar e passar o array.
Risco de divergência entre notebook e `ml/src` é mitigado por estarem documentados lado a lado.

## ADR-022 — Carregamento lazy e cache do modelo no backend

**Contexto:** importar o TensorFlow (~1 GB de dependências já instaladas) tem custo de tempo, e o
backend não deve pagar esse custo quando o modelo ainda não existe.

**Decisão:** o serviço importa `keras` apenas quando há pesos publicados, cacheia o modelo com um
lock de thread e invalida o cache pelo `mtime` do arquivo (novo treino → recarga automática).

**Consequência:** `/health` e o restante da API seguem rápidos sem modelo; publicar novos pesos
não exige reinício do processo. `reset_cache()` é usado nos testes.

## ADR-023 — `needs_human_review` quando não há modelo

**Contexto:** na FASE 1 toda ocorrência com foto ficava sinalizada para revisão porque o modelo não
existia. Com a FASE 3, o comportamento passa a depender de existir ou não pesos publicados.

**Decisão:** manter a regra existente — sem modelo, `needs_human_review=true`; com modelo, a
revisão é determinada pela confiança versus `CONFIDENCE_THRESHOLD` (docs/BUSINESS_RULES.md §6).

**Consequência:** o comportamento é progressivo e honesto: antes do treino tudo é "revisão humana";
depois, apenas as classificações duvidosas.