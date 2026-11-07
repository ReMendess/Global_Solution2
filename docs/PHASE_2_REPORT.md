# PHASE_2_REPORT.md — Frontend Expo e dashboard

> Relatório de fechamento da FASE 2. Números e resultados vêm de execução real dos comandos
> indicados, não de estimativa.

## 1. Escopo executado

Aplicação Expo (SDK 57) com Expo Router + React Native Web consumindo exclusivamente a API REST
construída na FASE 1. Inclui telas do cidadão e da administração, layout responsivo, alternância de
perfil e testes automatizados.

Nada de fases futuras foi antecipado: **não** existe tela de chat do agente (FASE 6) nem de execuções
do RPA (FASE 5); os indicadores exibidos vêm apenas de rotas já implementadas.

## 2. Arquivos criados

```
frontend/package.json, app.json, tsconfig.json, .env.example, README.md, .gitignore
frontend/src/app/_layout.tsx, +not-found.tsx, index.tsx, registrar.tsx, consultar.tsx
frontend/src/app/admin/_layout.tsx, dashboard.tsx, ocorrencias.tsx,
                    admin/ocorrencias/[id].tsx, conteineres.tsx
frontend/src/components/{screen,card,badge,button,text-field,choice-chips,states,
                         occurrence-list-item,occurrence-form,app-nav,profile-switch,
                         admin-gate}.tsx
frontend/src/constants/theme.ts
frontend/src/hooks/use-async.ts
frontend/src/lib/{format,validation}.ts (+ testes)
frontend/src/services/{config,api-client,api,occurrence-form}.ts (+ testes)
frontend/src/state/profile-context.tsx
frontend/src/types/domain.ts
```

**Modificados no backend:** `backend/app/main.py` (montagem de `/uploads`),
`backend/tests/test_uploads.py` (novo, 2 testes).

## 3. Decisões técnicas

| Tema | Decisão |
|---|---|
| SDK | Expo **57** por compatibilidade com o Expo Go (ADR-016) |
| Template | `blank-typescript` em vez do `default` cheio de demos (ADR-017) |
| URL da API | `EXPO_PUBLIC_API_URL` → host do Metro → fallback local (ADR-020, testado) |
| Imagens | `GET /uploads/{arquivo}` servido pelo FastAPI (ADR-018) |
| Perfil | `ProfileProvider` + cabeçalho `X-User-Role` (ADR-019) |
| Estado de dados | hook próprio `useAsync` (loading/erro/reload) sem dependência extra |
| Multipart | `toUploadPart` converte para `Blob` na web e `{uri,name,type}` no nativo |
| Layout | `Screen` com largura máxima no desktop e grades que colapsam no mobile |

## 4. Testes automatizados (frontend)

```
cd frontend; npm test
Test Suites: 6 passed, 6 total
Tests:       46 passed, 46 total
```

| Suíte | Testes | Foco |
|---|---|---|
| `services/api-client.test.ts` | 6 | JSON, FormData sem Content-Type, `X-User-Role`, 409 com `detail`, falha de rede, 204 |
| `services/config.test.ts` | 8 | extração de host, prioridade da URL, URL de upload |
| `services/occurrence-form.test.ts` | 5 | conversão web/nativo, campos opcionais, coordenadas inválidas |
| `lib/validation.test.ts` | 10 | limites do formulário, protocolo, coordenadas |
| `lib/format.test.ts` | 10 | rótulos pt-BR, datas, confiança, horas, ocupação |
| `components/components.test.tsx` | 7 | render de `Badge`, `StatusBadge`, `PriorityBadge`, `Button`, `ProgressBar` |

**Backend após a fase:** `python -m pytest` → **91 passed**; `ruff check` e `ruff format --check`
sem erros.

## 5. Verificação de execução real

```
cd frontend; npm run typecheck   -> sem erros
cd frontend; npm run build:web   -> Web Bundled 21830ms (808 módulos) | Exported: dist
cd frontend; npm run web         -> Waiting on http://localhost:8081
```

Com o Metro e o backend rodando:

| Verificação | Resultado |
|---|---|
| `GET http://localhost:8081/` | `200`, 1.291 bytes de HTML |
| `GET .../entry.bundle?platform=web&dev=true` | `200`, 4.165.308 bytes |
| Bundle contém `Smart Clean City` | sim |
| Bundle contém `Registrar ocorrência` | sim |
| Bundle contém `dashboard/summary` | sim |
| Bundle contém `X-User-Role` | sim |
| `OPTIONS /api/v1/meta/enums` com `Origin: http://localhost:8081` | `200`, `access-control-allow-origin: *` |
| `GET /api/v1/dashboard/summary` com `X-User-Role: ADMIN` | `200`, `total_occurrences: 7` |
| `GET /uploads/{arquivo}` (teste automatizado) | `200`, `image/png`, tamanho igual ao gravado |

## 6. Critérios de aceite — situação

- [x] Aplicação web servida pelo Metro em `http://localhost:8081`
- [x] Bundle web compila e inclui as chamadas reais à API
- [x] CORS liberado para a origem do frontend
- [x] `typecheck` limpo e 46 testes passando
- [x] Backend com `/uploads` e 91 testes passando
- [ ] Registro/consulta validados por interação no navegador — **exige execução manual**; a lógica
      está coberta por testes, mas a interação visual não foi exercitada nesta sessão
- [ ] Execução no Expo Go — **exige celular** com o app instalado

## 7. Limitações identificadas

1. **Validação visual manual pendente:** não há navegador headless disponível nesta fase
   (Playwright entra na FASE 5), então cliques e formulário não foram exercitados automaticamente.
2. **Perfil forjável:** `X-User-Role` vem do cliente; sem autenticação real até a FASE 7.
3. **Perfil não persistido:** recarregar a página volta o perfil para cidadão (estado em memória).
4. **Chat do agente ausente:** depende da FASE 6 no backend.
5. **Sem execuções do RPA na UI:** depende da FASE 5.
6. **Imagens sem controle de acesso:** qualquer pessoa com o nome do arquivo acessa `/uploads/...`.
7. **Câmera na web:** o botão "Tirar foto" aparece apenas no nativo; na web usa-se a galeria/seleção
   de arquivo (limitação do `expo-image-picker` na plataforma).
8. **Testes de componente** cobrem apenas componentes puros; telas completas dependem de navegador.
9. **`needs_human_review` sempre verdadeiro** enquanto o modelo não existir (FASE 3).

## 8. Próximo passo

**FASE 3 — MobileNetV2:** entregar o pipeline em `ml/src/` e o notebook para execução no
**Google Colab** (ADR-013), com métricas reais, e trocar o stub de `classification_service` pela
inferência dos pesos treinados, expondo `/api/v1/classification/*`.