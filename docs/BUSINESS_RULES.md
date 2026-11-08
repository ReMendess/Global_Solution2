#  Regras de negócio


## 1. Categorias de ocorrência

| Valor | Significado |
|---|---|
| `ILLEGAL_DUMPING` | Descarte irregular |
| `OVERFLOW` | Transbordamento de contêiner |
| `DAMAGED_CONTAINER` | Contêiner danificado |
| `OTHER` | Não classificável ou fora das categorias |

## 2. Classes do modelo

O modelo classifica a **imagem**:

| Valor | Significado |
|---|---|
| `REGULAR` | Situação de descarte regular |
| `IRREGULAR` | Situação irregular detectada |

A categoria é o resutlado da combinação `model_label` + `confidence` + informação do cidadão. O
`model_label` .

## 3. Status e máquina de estados

```
OPEN ──▶ CLASSIFIED ──▶ PENDING_DISPATCH ──▶ DISPATCHED ──▶ IN_PROGRESS ──▶ RESOLVED
  │            │                  │
  └────────────┴──────────────────┴──────────▶ REJECTED
```


## 5. Alertas de ocupação de contêiner

| Ocupação | `alert_level` |
|---|---|
| menor que 80% | `NORMAL` |
| de 80% até 89% | `HIGH` |
| 90% ou mais | `CRITICAL` |


## 8. Agente conversacional

- Interpretação por intenções + regras.
- Ferramentas: `consultar_ocorrencia`, `consultar_container`, `listar_pontos_coleta`,
  `criar_ocorrencia`, `consultar_indicadores`.
- Toda resposta deve derivar de dados. Sem dado disponível, a resposta vai declarar isso.
- Intenção não reconhecida → resposta de orientação com exemplos de perguntas válidas.
- Contexto por sessão: guarda a última ocorrência para permitir continuidade.
- Toda interação é persistida em `agent_interactions`.

## 9. Segurança e governança

| Regra | Como é aplicada |
|---|---|
| Controlar acesso por perfil | Perfil `ADMIN` exigido nas rotas administrativas |
| Minimizar dados pessoais | Sem CPF, telefone ou endereço completo obrigatório |
| Proteger imagens identificáveis | Upload restrito a imagem; nome de arquivo gerado pelo servidor |
| Registrar execuções do RPA | Tabela `rpa_executions` |
| Registrar resultado e versão do modelo | `model_label`, `confidence`, `model_version` |
| Evitar duplicidade | `dedup_hash` (ver `DATA_MODEL.md` §5) |
| Não expor credenciais | Apenas `.env` (ignorado) + `.env.example` |
