# E05 · Esqueleto do front-end

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Criar o esqueleto do front-end: Vite, shadcn sobre Base UI, roteador com placeholders, QueryClient e store da sessão.

## Arquivos permitidos

tudo em `frontend/`, exceto `src/styles/theme.css`, `src/lib/copy.ts` e `src/features/`: `package.json`, `pnpm-lock.yaml`, `vite.config.ts`, `vitest.config.ts`, `tsconfig*.json`, `eslint.config.js`, `.prettierrc`, `components.json`, `index.html`, `src/main.tsx`, `src/app/router.tsx`, `src/app/providers.tsx`, `src/app/layout.tsx`, `src/styles/index.css`, `src/lib/cn.ts`, `src/stores/session-store.ts`, `src/components/ui/*` (gerados pelo shadcn), `src/test/setup.ts`, `src/mocks/handlers.ts` (vazio), `src/app/router.test.tsx`, `public/illustrations/` (6 SVGs simples: `apartment-1..3.svg`, `house-1..3.svg`, desenhos geométricos de um prédio e de uma casa em 3 cores do tema).

## Dependências

E01, A01 (`theme.css`)

## Especificação

- **Passos:** gerar o template como manda "Procedimento obrigatório", logo abaixo; copiar dependências e scripts do `package.json` de referência (seção 2), aplicando as regras e os cortes dela; `pnpm dlx shadcn@latest init` escolhendo Base UI; `shadcn add button card badge progress slider select radio-group tabs tooltip switch skeleton sonner checkbox input label form`; `index.css` só com `@import "tailwindcss"; @import "tw-animate-css"; @import "./theme.css";`, apagando as variáveis e o `@theme` que o `shadcn init` gravar nesse arquivo, porque substituiriam o tema, e `@fontsource-variable/geist` importado em `main.tsx`; alias `@/` para `src/`; proxy `/api` para `http://localhost:8000` no `vite.config.ts`.
- **Router:** rotas `/`, `/coleta`, `/comecar`, `/demo`, `/comparar`, `/feed`, `/modelo`, `/experimento` apontando para um componente temporário `Placeholder` que mostra o nome da rota; rota `*` para a início.
- **`QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`.
- **`session-store.ts`:** Zustand com `persist` (chave `imobscore-session`, `localStorage` envolvido em `try/catch`): `{ sessionId: string | null, mode: "product" | "demo" | "collection" | null, setSession(id, mode), reset() }`.

## Procedimento obrigatório

Decisão de João (Q4): `frontend/` já tem os `.gitkeep` da E01 e os arquivos do arquiteto `src/styles/theme.css` e `src/lib/copy.ts`. **Nunca rode `pnpm create vite` dentro do repositório nem remova o que já existe.** Gere o template em uma pasta temporária e copie sem sobrescrever nada. Rode a partir da raiz do repositório:

```bash
T=$(mktemp -d) && (cd "$T" && pnpm create vite frontend --template react-ts --no-interactive)
cp -r --update=none "$T/frontend/." frontend/ && rm -rf "$T"
rm -f frontend/.oxlintrc.json
```

O template atual (create-vite 9) vem com Oxlint. Este projeto usa ESLint: apague `.oxlintrc.json` e substitua as dependências e os scripts do `package.json` pelos da referência abaixo. As pastas em `src/features/` continuam com o `.gitkeep`.

Por último, apague os `.gitkeep` das pastas que passaram a ter outros arquivos:

```bash
find frontend -path '*/node_modules' -prune -o -name .gitkeep -type f -exec sh -c '[ "$(ls -A "$(dirname "$1")" | wc -l)" -gt 1 ] && rm "$1"; true' _ {} \;
```

## Verificação

`pnpm build && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run` (o teste do router confere que `/feed` renderiza o placeholder).

## Regras gerais

- Todo código numérico recebe um `numpy.random.Generator` com semente explícita. Nada usa o estado global de `np.random`.
- Textos da interface em português do Brasil. Nomes de código, tabelas e colunas em inglês.
- Os dados do catálogo são simulados, e a interface diz isso ("catálogo de demonstração").
- Nada depende de internet em execução: sem CDN, sem fontes remotas e sem imagens externas. A única exceção são os mockups em `docs/mockups/`, que não fazem parte do app.
- Claude, ao encontrar uma decisão não prevista, escolhe a opção mais simples compatível com o plano e registra uma linha em `docs/decisions.md`. O executor não decide: pergunta (1.5).
- Ao fim de cada tarefa, o dono atualiza `docs/STATUS.md`.

**Dependências que travam o trabalho.** E05 espera A01 (precisa de `theme.css`). E06 espera A02. E07 espera A03 (`seed_for` e `random_pairs`). E08 espera M1 e M4 aprovados. E10 espera A06 marcada como concluída em `docs/STATUS.md`. E11 a E14 esperam G2. Se uma dependência atrasar, o executor passa para a próxima tarefa sem dependência pendente e registra o atraso em `docs/STATUS.md`.

- Apagar o `.gitkeep` de uma pasta que passou a ter outros arquivos faz parte da tarefa, mesmo sem constar em "Arquivos permitidos".

## Contexto do plano

Trechos copiados de `docs/PLAN.md`. Menções a "seção N" se referem ao plano, e o necessário para esta tarefa está aqui. Se um trecho conflitar com as partes acima deste título, valem as de cima.

### Seção 2 · Stack do front-end

A base do front-end segue a stack que o autor já usou em outro projeto (`package.json` de referência abaixo). As versões da tabela são o mínimo. As linhas marcadas com ➕ não estavam nessa stack e foram acrescentadas para necessidades específicas do ImobScore.

| Ferramenta | Versão mínima | Para quê |
| --- | --- | --- |
| Node.js | 24 LTS | Ambiente de build (casa com `@types/node` 24) |
| pnpm | atual | Gerenciador de pacotes |
| TypeScript | \~6.0, `strict` | Linguagem; build com `tsc -b` (project references) |
| React + React DOM | 19.2 | Interface |
| Vite + `@vitejs/plugin-react` | 8.2 / 6.1 | Dev server e bundle |
| React Router (`react-router-dom`) | 7.18 (modo declarativo) | Rotas |
| TanStack Query | 5.102 | Requisições, cache, `useInfiniteQuery` no feed |
| Zod | 4.5 | Schemas de formulário e checagem de respostas críticas |
| React Hook Form + `@hookform/resolvers` | 7.87 / 5.9 | Formulários (onboarding, coleta e vistoria) |
| Tailwind CSS + `@tailwindcss/vite` | 4.3 | Estilização |
| shadcn (CLI e pacote) sobre Base UI (`@base-ui/react`) | 4.20 / 1.7 | Componentes acessíveis copiados para o repositório, com primitivos do Base UI em vez de Radix |
| `class-variance-authority` + `clsx` + `tailwind-merge` | 0.7 / 2.1 / 3.6 | Variantes de componentes e a função `cn()` |
| `tw-animate-css` | 1.4 | Animações de entrada e saída dos componentes do shadcn |
| Framer Motion | 13.2 | Animação dos cartões de comparação e da reordenação do feed (`layout`) |
| lucide-react | 1.40 | Ícones |
| `@fontsource-variable/geist` | 5.3 | Fonte Geist empacotada no build, sem depender de internet |
| ➕ openapi-typescript + openapi-fetch | atual | Tipos e cliente gerados do OpenAPI do FastAPI, para o front não redigitar os schemas da API |
| ➕ Recharts | atual | Gráficos do painel do modelo e do experimento |
| ➕ Zustand (com `persist`) | atual | Estado local pequeno: id da sessão e modo demo |
| Vitest + `@vitest/coverage-v8` + jsdom | 5.0 / 5.0 / 29 | Testes de componentes e cobertura |
| Testing Library (`react`, `jest-dom`, `user-event`) | 16.3 / 7.0 / 14.6 | Renderizar, consultar e simular clique e teclado |
| MSW | 2.15 | API simulada nos testes e no modo `dev:mock` do navegador |
| ➕ Playwright | atual | \[corte\] Não instalar no prazo curto; o teste offline é o roteiro manual da seção 9 |
| ESLint (flat config) + `typescript-eslint` + `eslint-plugin-react-hooks` + `eslint-plugin-react-refresh` + `globals` | 10.9 / 8.69 / 7.1 / 0.5 / 17 | Lint |
| Prettier (+ `prettier-plugin-tailwindcss`) | 3.9 | Formatação; o plugin ➕ ordena as classes do Tailwind |

O estado do servidor fica só no TanStack Query. O Zustand guarda apenas o que é do navegador: `sessionId`, a flag do modo demo e a última rota. Os tipos da API não são escritos à mão. O comando `pnpm gen:api` lê `http://localhost:8000/openapi.json` e gera `src/api/schema.d.ts`, que vai para o Git.

**Avaliação da stack de referência.** Ela casa bem com o plano e foi adotada quase inteira. As trocas em relação à versão anterior deste plano foram:

- **ESLint + Prettier no lugar do Biome**, porque o autor já conhece essa configuração e o `eslint-plugin-react-hooks` 7 traz as regras do React Compiler.
- **Base UI no lugar do Radix** como base do shadcn. É a opção mais nova que o shadcn oferece e já estava em uso pelo autor. Ao rodar `shadcn init`, escolher Base UI.
- **Geist no lugar da Inter**, empacotada pelo Fontsource.
- **Node 24 LTS no lugar do Node 22**, para casar com `@types/node` 24.

Quatro itens foram acrescentados, cada um com um motivo do ImobScore: openapi-typescript e openapi-fetch (tipos da API sem redigitar), Recharts (painéis do modelo e do experimento), Zustand (sessão anônima persistida) e Playwright (o teste offline da demo). O `prettier-plugin-tailwindcss` é opcional. Nada da stack de referência foi descartado.

**`package.json` de referência do front-end** (o agente usa estas versões como mínimo e completa as marcadas com ➕):

```json
{
  "name": "imobscore-web",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "engines": { "node": ">=24" },
  "scripts": {
    "dev": "vite",
    "dev:mock": "VITE_MOCK_API=1 vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint .",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,css}\"",
    "typecheck": "tsc -b --noEmit",
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "e2e": "playwright test",
    "gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/api/schema.d.ts"
  },
  "dependencies": {
    "@base-ui/react": "^1.7.0",
    "@fontsource-variable/geist": "^5.3.0",
    "@hookform/resolvers": "^5.9.1",
    "@tanstack/react-query": "^5.102.8",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "framer-motion": "^13.2.0",
    "lucide-react": "^1.40.0",
    "openapi-fetch": "➕ atual",
    "react": "^19.2.8",
    "react-dom": "^19.2.8",
    "react-hook-form": "^7.87.0",
    "react-router-dom": "^7.18.3",
    "recharts": "➕ atual",
    "shadcn": "^4.20.1",
    "tailwind-merge": "^3.6.0",
    "tw-animate-css": "^1.4.0",
    "zod": "^4.5.4",
    "zustand": "➕ atual"
  },
  "devDependencies": {
    "@eslint/js": "^10.0.1",
    "@playwright/test": "➕ atual",
    "@tailwindcss/vite": "^4.3.3",
    "@testing-library/jest-dom": "^7.0.1",
    "@testing-library/react": "^16.3.3",
    "@testing-library/user-event": "^14.6.7",
    "@types/node": "^24.13.3",
    "@types/react": "^19.2.18",
    "@types/react-dom": "^19.2.4",
    "@vitejs/plugin-react": "^6.1.0",
    "@vitest/coverage-v8": "^5.0.3",
    "eslint": "^10.9.1",
    "eslint-plugin-react-hooks": "^7.1.1",
    "eslint-plugin-react-refresh": "^0.5.6",
    "globals": "^17.12.0",
    "jsdom": "^29.1.1",
    "msw": "^2.15.0",
    "openapi-typescript": "➕ atual",
    "prettier": "^3.9.6",
    "prettier-plugin-tailwindcss": "➕ atual",
    "tailwindcss": "^4.3.3",
    "typescript": "~6.0.2",
    "typescript-eslint": "^8.69.0",
    "vite": "^8.2.2",
    "vitest": "^5.0.0"
  },
  "msw": { "workerDirectory": ["public"] }
}
```

**Regras para o agente sobre esse pacote**

- Os valores "➕ atual" são marcadores. Na instalação, o executor roda `pnpm add <pacote>` (ou `pnpm add -D` para devDependencies) e deixa a versão real no `package.json` e no lockfile.
- **Cortes no prazo curto (1.7):** não instalar `@playwright/test`, não criar os scripts `e2e` e `dev:mock` e não configurar o worker do MSW no navegador. O MSW roda só no Node, dentro dos testes do Vitest (`msw/node`). Remover a chave `"msw"` do `package.json`.
- Importar as rotas de `react-router-dom`, sem misturar com imports de `react-router`.
- `vitest.config.ts` com `environment: "jsdom"` e `setupFiles: ["src/test/setup.ts"]`. O `setup.ts` importa `@testing-library/jest-dom/vitest` e liga o servidor do MSW (`setupServer(...handlers)` de `src/mocks/handlers.ts`) antes de todos os testes, reseta os handlers depois de cada teste e o desliga no fim. Sem limite mínimo de cobertura.

### Seção 3 · Estrutura do front-end

```text
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── eslint.config.js
    ├── .prettierrc
    ├── Dockerfile
    ├── nginx.conf
    ├── public/illustrations/ # SVGs locais por tipo de imóvel
    └── src/
        ├── main.tsx
        ├── app/              # router.tsx providers.tsx layout.tsx
        ├── api/              # schema.d.ts (gerado) client.ts queries.ts
        ├── features/
        │   ├── onboarding/
        │   ├── compare/
        │   ├── feed/
        │   ├── listing/
        │   ├── model-panel/
        │   └── experiment/
        ├── components/ui/    # shadcn/ui
        ├── lib/              # copy.ts (textos, dono A), format.ts (Intl pt-BR), cn.ts
        ├── mocks/            # handlers.ts do MSW (só testes)
        ├── test/             # setup.ts do Vitest
        ├── stores/           # session-store.ts (Zustand)
        └── styles/           # index.css (E) e theme.css (dono A)
```

### Seção 1.7 · Escopo no prazo curto

**Essencial (não corta):** o motor completo (seções 5.1 a 5.9) com testes; a coleta e a avaliação com dados reais, ou simulados e declarados como tal; o fluxo da demo (persona, 3 pares, feed com Antes e Depois); os painéis do modelo e do experimento; e a execução offline.

**Já cortado (não implementar):**

| Item | Onde aparecia | O que fica no lugar |
| --- | --- | --- |
| Rolagem infinita do feed | 7 | Uma consulta só, com `limit=30` |
| Aba Lado a lado | 7 | A alternância Antes e Depois |
| Recompensa com feed ao fim da coleta | 7 | Tela de agradecimento |
| GitHub Actions e pre-commit | 2 | `make check` rodado no notebook (seção 9) |
| Playwright | 2, 9 | Roteiro manual offline (seção 9) |
| `dev:mock` no navegador | 2 | MSW só nos testes |
| Cobertura mínima no front-end | 2 | Testes dos fluxos críticos listados em cada tarefa |

**Cortes condicionais**, nesta ordem, decididos por João em 09/11 às 12h:

| Corte | O que sai | O que fica |
| --- | --- | --- |
| C1 · já aplicado, reversível | Detalhe do imóvel e vistoria (M8, tarefa E17) | Cartão do feed sem link |
| C2 | Motivos "por que este imóvel" no cartão | Score e intervalo |
| C3 | Escolha adaptativa de pares (BALD) | Pares aleatórios também na demo |
| C4 | Gráfico de traço das cadeias no painel do modelo | Quadro de diagnósticos |

### Seção 7 · Dados e estado

- **Cliente:** `openapi-fetch` com o tipo `paths` de `src/api/schema.d.ts` e `baseUrl: "/api/v1"`. No dev, o Vite faz proxy de `/api` para `http://localhost:8000`.
- **Chaves de query:** `['meta', 'options']`, `['meta', 'personas']`, `['session', id]`, `['pair', id]`, `['feed', id, method, at]`, `['posterior', id, n]`, `['trace', id, n, feature]`, `['listing', id, sessionId]`, `['experiment', runId]`. Todas ficam em `src/api/queries.ts` como funções `queryOptions(...)`.
- **Padrões do `QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`. Dados de `meta` usam `staleTime: Infinity`, porque não mudam durante a sessão.
- **Depois de responder um par:** invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
- **Zustand:** `{ sessionId, mode, setSession, reset }`, com `persist` no `localStorage` dentro de `try/catch`. Sem `sessionId` válido, as rotas protegidas redirecionam para `/comecar`.

### Seção 7 · Visual e acessibilidade

- Componentes do shadcn/ui, sobre Base UI: `Button`, `Card`, `Badge`, `Progress`, `Slider`, `Select`, `RadioGroup`, `Tabs`, `Tooltip`, `Switch`, `Skeleton`, `Sonner` (avisos).
- Fonte Geist instalada via `@fontsource-variable/geist`, para funcionar offline. Nada de Google Fonts.
- Cores como variáveis CSS do tema do shadcn, com modo escuro. O selo de score tem três faixas (0 a 39, 40 a 69, 70 a 100) e sempre mostra o número, para não depender só da cor.
- Valores com `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 })`.
- Contraste AA, foco visível, `aria-live="polite"` na barra de progresso e textos alternativos nas ilustrações.
- Estados de carregamento com `Skeleton`, e erros com aviso e botão "Tentar de novo". Um `ErrorBoundary` na raiz mostra uma tela de erro amigável.
