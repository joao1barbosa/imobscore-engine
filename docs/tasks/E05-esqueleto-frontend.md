# E05 · Esqueleto do front-end

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Criar o esqueleto do front-end: Vite, shadcn sobre Base UI, roteador com placeholders, QueryClient e store da sessão.

## Arquivos permitidos

tudo em `frontend/`, exceto `src/styles/theme.css`, `src/lib/copy.ts` e `src/features/`: `package.json`, `pnpm-lock.yaml`, `vite.config.ts`, `vitest.config.ts`, `tsconfig*.json`, `eslint.config.js`, `.prettierrc`, `components.json`, `index.html`, `src/main.tsx`, `src/app/router.tsx`, `src/app/providers.tsx`, `src/app/layout.tsx`, `src/styles/index.css`, `src/lib/cn.ts`, `src/stores/session-store.ts`, `src/components/ui/*` (gerados pelo shadcn), `src/test/setup.ts`, `src/mocks/handlers.ts` (vazio), `src/app/router.test.tsx`, `public/illustrations/` (6 SVGs simples: `apartment-1..3.svg`, `house-1..3.svg`, desenhos geométricos de um prédio e de uma casa em 3 cores do tema).

## Dependências

E01, A01 (`theme.css`)

## Especificação

- **Passos:** `pnpm create vite frontend --template react-ts`; copiar dependências e scripts do `package.json` de referência (seção 2), aplicando as regras e os cortes dela; `pnpm dlx shadcn@latest init` escolhendo Base UI; `shadcn add button card badge progress slider select radio-group tabs tooltip switch skeleton sonner checkbox input label form`; `index.css` com `@import "tailwindcss"; @import "tw-animate-css"; @import "./theme.css";` e `@fontsource-variable/geist` importado em `main.tsx`; alias `@/` para `src/`; proxy `/api` para `http://localhost:8000` no `vite.config.ts`.
- **Router:** rotas `/`, `/coleta`, `/comecar`, `/demo`, `/comparar`, `/feed`, `/modelo`, `/experimento` apontando para um componente temporário `Placeholder` que mostra o nome da rota; rota `*` para a início.
- **`QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`.
- **`session-store.ts`:** Zustand com `persist` (chave `imobscore-session`, `localStorage` envolvido em `try/catch`): `{ sessionId: string | null, mode: "product" | "demo" | "collection" | null, setSession(id, mode), reset() }`.

## Verificação

`pnpm build && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run` (o teste do router confere que `/feed` renderiza o placeholder).

## Atenção

`pnpm create vite frontend` encontra uma pasta que já existe: tem os `.gitkeep` da E01 e, por depender da A01, também `src/styles/theme.css` e `src/lib/copy.ts`. Nunca escolha remover os arquivos existentes. Ver a pergunta Q4 em `docs/STATUS.md`.
