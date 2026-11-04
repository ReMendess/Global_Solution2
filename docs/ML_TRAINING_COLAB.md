# ML_TRAINING_COLAB.md — Como treinar o modelo (Google Colab)

> Este é o roteiro para **você** executar o treinamento do MobileNetV2 no Google Colab
> (ADR-013). O Cline já entregou o notebook pronto: `ml/notebooks/cidade_limpa_mobilenetv2.ipynb`.
> Siga os passos abaixo na ordem.

## 1. O que você vai produzir

| Arquivo | Conteúdo | Destino local |
|---|---|---|
| `cidade_limpa_mobilenetv2.keras` | pesos do modelo treinado | `ml/models/` |
| `cidade_limpa_mobilenetv2.metadata.json` | versão, classes, métricas reais | `ml/models/` |
| `relatorio_treinamento.json` | relatório detalhado | `ml/reports/` (opcional) |
| matriz de confusão (imagem) | visualização das métricas | `ml/reports/` (opcional) |

## 2. Abrir o notebook no Colab

1. Acesse <https://colab.research.google.com/> e faça login com sua conta Google.
2. **Arquivo → Fazer upload de notebook** e envie
   `ml/notebooks/cidade_limpa_mobilenetv2.ipynb`.
3. **Ambiente de execução → Alterar tipo de ambiente → Acelerador de hardware → GPU** e salve.

## 3. O dataset (a parte que depende de você)

O modelo classifica **duas classes**:

- `REGULAR` — descarte regular (lixo acondicionado, lixeiras organizadas, reciclagem);
- `IRREGULAR` — descarte irregular (entulho, transbordamento, lixo em via pública).

Você precisa de imagens reais. Três opções (todas descritas no notebook, seção 1):

**Opção A — seu próprio ZIP**
Monte um `.zip` com duas pastas `REGULAR/` e `IRREGULAR/` e envie pelo notebook.

**Opção B — Google Drive**
Suba as pastas para o Drive e monte-o no Colab.

**Opção C — dataset público (Kaggle)**
Exemplos que mapeiam bem para o problema:

1. **"Garbage Classification" (Kaggle, 12 classes, ~15k imagens)** — mapeie classes de lixo
   acondicionado/reciclável para `REGULAR` e entulho/despejo para `IRREGULAR`.
2. **"Waste Segregation Image Dataset" (Kaggle)** — idem.

> Recomendação de qualidade: **100+ imagens por classe** (mínimo para o notebook rodar: 10).
> Quanto mais balanceado e representativo, melhor o resultado.

## 4. Executar as células

Rode **todas as células na ordem** (Ambiente de execução → Executar tudo). O notebook:

1. valida o dataset (seção 1);
2. divide em treino/validação/teste (seção 2);
3. constrói o MobileNetV2 (seção 3);
4. treina a cabeça (seção 4) e ajusta fino (seção 5);
5. avalia no teste e imprime **accuracy, precision, recall, F1 e matriz de confusão** (seção 6);
6. salva e **baixa automaticamente** os artefatos (seção 7).

## 5. Publicar o modelo no repositório

Depois de baixar os arquivos, coloque-os assim:

```
Global_Solution2/
├── ml/
│   ├── models/
│   │   ├── cidade_limpa_mobilenetv2.keras          ← pesos
│   │   └── cidade_limpa_mobilenetv2.metadata.json  ← metadados/métricas
│   └── reports/
│       ├── relatorio_treinamento.json              ← opcional
│       └── (matriz de confusão)                    ← opcional
```

> Esses arquivos ficam fora do git (`.gitignore`), que é o comportamento correto:
> pesos treinados não são versionados.

## 6. Verificar a integração

```powershell
# backend
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Confira:

- `GET http://127.0.0.1:8000/health` → `"model_loaded": true`;
- `GET /api/v1/classification/model-info` → versão `mobilenetv2-v1` + métricas reais;
- `POST /api/v1/classification/predict` (multipart `image`) → rótulo + `probabilities`.

A partir daí, o **registro de ocorrência com foto** passa a preencher `model_label`,
`confidence` e `model_version` automaticamente, alimentando o dashboard.

## 7. Perguntas frequentes

**E se eu não tiver as 100 imagens por classe?**
O notebook roda com menos (mínimo 10), mas avisa que a acurácia tende a ser baixa. Os
números que aparecerem serão publicados como estão — nunca inventamos métricas.

**Preciso ajustar hiperparâmetros?**
Os padrões seguem `ml/src/config.py`. Para começar, deixe como está; ajuste `EPOCHS_*`
ou `BATCH_SIZE` só se o treino for muito lento ou estourar a memória.

**O notebook não importa o repositório. Por quê?**
O repositório é privado e o Colab não tem as credenciais. O notebook é autocontido e
replica o mesmo pipeline de `ml/src/` (mesmos hiperparâmetros, mesma ordem de classes).

**Preciso treinar de novo se melhorar o dataset?**
Sim — cada rodada gera novos pesos e um novo `metadata.json`. Basta substituir os dois
arquivos em `ml/models/` e reiniciar o backend (o serviço recarrega automaticamente
quando os pesos mudam).
