# Cidade Limpa — Frontend (Expo + React Native Web)

Aplicação do cidadão e da administração, consumindo **exclusivamente** a API REST do backend
(`backend/`, FastAPI). Desenvolvida com Expo (SDK 57), Expo Router e React Native Web.

## Requisitos

- Node.js 22 (verificado: 22.17.0) e npm 10 (verificado: 10.9.2).
- Backend em execução em `http://127.0.0.1:8000` (`cd backend; python -m uvicorn app.main:app --port 8000`).
- Expo Go no celular (SDK 57) para testar no dispositivo.

## Instalação

```powershell
cd frontend
npm install
```

## Como executar

```powershell
# Web (React Native Web) — http://localhost:8081
npm run web

# Mobile com Expo Go (leia o QR Code)
npm start
```

A URL da API é resolvida automaticamente:

1. `EXPO_PUBLIC_API_URL` (veja `.env.example`), se definida;
2. host do servidor Metro + porta 8000 (funciona no Expo Go e na web);
3. fallback `http://127.0.0.1:8000`.

> No celular, o app usa o IP da máquina na rede local. O backend precisa aceitar conexões nesse IP
> (`--host 0.0.0.0`) e o firewall deve permitir a porta 8000.

## Scripts

| Script | Descrição |
|---|---|
| `npm start` | Servidor de desenvolvimento (Expo) |
| `npm run web` | Servidor de desenvolvimento para navegador |
| `npm run android` / `npm run ios` | Abre no emulador/dispositivo |
| `npm run typecheck` | `tsc --noEmit` |
| `npm test` | Testes com Jest (`jest-expo`) |
| `npm run build:web` | Exporta o bundle web em `dist/` |

## Estrutura

```
src/
├── app/                 # rotas (Expo Router)
│   ├── _layout.tsx      # providers + navegação
│   ├── index.tsx        # página inicial do cidadão
│   ├── registrar.tsx    # registro de ocorrência (foto + protocolo)
│   ├── consultar.tsx    # consulta por protocolo
│   └── admin/           # dashboard, ocorrências, contêineres
├── components/          # UI reutilizável (screen, card, badge, fields...)
├── constants/theme.ts   # paleta, espaçamentos e breakpoints
├── hooks/use-async.ts   # carregamento/erro/reload
├── lib/                 # formatação pt-BR e validação
├── services/            # cliente HTTP, endpoints e montagem do multipart
├── state/               # perfil da sessão (cidadão/administrador)
└── types/domain.ts      # tipos espelhando os schemas do backend
```

## Perfil de acesso

O backend identifica o perfil pelo cabeçalho `X-User-Role`. No app, use o botão
**Entrar como admin** (canto superior direito) para alternar entre cidadão e administrador.
Não há autenticação real nesta fase (ver `docs/DECISIONS.md`, ADR-014).

## Testes

```powershell
npm test
```

Cobrem o cliente HTTP (cabeçalhos, erros, multipart), a resolução da URL da API, formatação,
validação do formulário e a renderização dos componentes principais.

## Limitações conhecidas

- Perfil demonstrativo por cabeçalho (sem senha/JWT).
- Sem tela de chat do agente: depende da FASE 6 do backend.
- Imagens exibidas via `GET /uploads/{arquivo}` servido pelo backend.