# PHASE_3_REPORT.md — MobileNetV2 e visão computacional

> Relatório de fechamento da FASE 3. Números e resultados vêm de execução real dos comandos
> indicados — com uma ressalva explícita: o **treinamento** é executado pelo autor no Google Colab
> (ADR-013) e, portanto, as métricas finais ficam pendentes dessa execução.

## 1. Escopo executado

Pipeline de ML reprodutível, notebook para o Colab e integração da inferência no backend. A parte
que depende do meu ambiente (código, testes, build do modelo, rotas) foi feita e verificada; a parte
que depende de GPU e de um dataset real fica documentada em `docs/ML_TRAINING_COLAB.md`.

## 2. Arquivos criados

```
ml/__init__.py
ml/src/__init__.py, config.py, dataset.py, preprocess.py, model.py, evaluate.py, train.py
ml/notebooks/cidade_limpa_mobilenetv2.ipynb
backend/app/schemas/classification.py
backend/app/api/routes/classification.py
backend/app/services/classification_service.py   (reescrito)
backend/tests/test_classification.py
docs/ML_TRAINING_COLAB.md, docs/PHASE_3_REPORT.md
```

**Modificados:** `backend/app/core/exceptions.py` (`ModelUnavailableError`),
`backend/app/core/config.py` (sem mudanças — já declarava `model_path`/`model_metadata_path`),
`backend/app/api/routes/__init__.py`, `backend/app/main.py`, `backend/app/schemas/__init__.py`,
`docs/{ROADMAP,API_SPEC,ENVIRONMENT,DECISIONS,README}.md`.

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| Treino | Google Colab (ADR-013); notebook autocontido que replica `ml/src/` (ADR-021) |
| Normalização | camada `Rescaling` interna ao modelo → backend envia pixels [0, 255] |
| Classes | ordem fixa `["REGULAR", "IRREGULAR"]`, softmax de 2 saídas |
| Inferência | carregamento lazy + cache por thread + invalidação por `mtime` (ADR-022) |
| Revisão humana | sem modelo → `true`; com modelo → `confidence < CONFIDENCE_THRESHOLD` (ADR-023) |
| Diagnóstico | `/predict` não persiste nada; o fluxo de ocorrência continua resiliente |
| Pipeline | `dataset`/`preprocess`/`model`/`evaluate`/`train` separados e testáveis |

## 4. Verificações reais executadas

```
python -m pytest                        → 102 passed (11 novos de classificação)
python -m ruff check .                  → All checks passed!
```

| Verificação | Resultado |
|---|---|
| Divisão do dataset (sintético 30+30) | `train 21/21`, `val 4/4`, `test 5/5`, `manifest.json` gerado |
| `build_model()` real (MobileNetV2/ImageNet) | entrada `(None,224,224,3)`, saída `(None,2)` |
| Parâmetros | cabeça 2.562 / total 2.260.546; ajuste fino libera 19 camadas (1.513.282 treináveis) |
| `GET /classification/model-info` sem pesos | `503` |
| `POST /classification/predict` com modelo de fixture | `200`, `label` + `probabilities` somando 1 |
| `POST /classification/predict` formato inválido | `422` |
| Ocorrência com foto + modelo de fixture | preenche `model_label`, `confidence`, `model_version` |
| Metadados ilegíveis | API não quebra; usa `"unavailable"` + classes padrão |

O modelo de fixture usado nos testes é **um Keras mínimo criado em runtime**, apenas para exercitar
o caminho real de carregamento → pré-processamento → inferência. Não é o modelo do projeto e **não
é apresentado como resultado de treinamento** (isso violaria a regra "não inventar métricas").

## 5. Critérios de aceite — situação

- [x] Pipeline de dataset (validação + divisão reprodutível) implementado e testado
- [x] Notebook Colab pronto, autocontido e com download automático dos artefatos
- [x] `GET /model-info` e `POST /predict` implementados (200 com modelo, 503 sem)
- [x] Registro de ocorrência segue tolerante à ausência/falha do modelo
- [x] Testes automatizados de classificação passando
- [ ] **Pesos treinados e métricas reais publicados** — pendente da execução no Colab pelo autor

## 6. Limitações identificadas

1. **Sem pesos reais ainda:** `model_loaded` segue `false` e toda ocorrência fica em revisão humana —
   esperado até você rodar o Colab.
2. **Acurácia depende do dataset:** com poucas imagens (10–99/classe) o modelo tende a ser fraco; o
   notebook avisa sobre isso.
3. **CPU local lenta:** treinar aqui seria demorado; por isso o treino é no Colab (GPU).
4. **`predict` sem autenticação/rate limit:** rota pública de diagnóstico, sem dados pessoais.
5. **Dependência TF no runtime:** só é importado quando há pesos, minimizando o custo.
6. **Sem monitoramento de drift:** o modelo não revalida periodicamente; a troca de pesos é manual
   (substituir os arquivos em `ml/models/`).

## 7. Próximo passo (você)

Siga `docs/ML_TRAINING_COLAB.md` para treinar no Colab e publicar os pesos em `ml/models/`. Assim que
os dois arquivos (`.keras` + `.metadata.json`) estiverem lá, a inferência real passa a funcionar sem
nenhuma mudança de código — basta reiniciar o backend (ou o serviço recarrega sozinho por mtime).

Paralelamente, eu posso seguir para a **FASE 4 (Simulador IoT)**.