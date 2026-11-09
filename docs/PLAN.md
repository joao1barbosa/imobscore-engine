# ImobScore — Plano de implementação

Nov 3, 2026 · @João

## 1. Contexto, prazo, papéis e regras

O MVP do ImobScore será construído de 04/11/2026 a 09/11/2026, com o código congelado em 09/11 às 22h e a apresentação na InovaTech em 11/11/2026. Dois agentes de IA dividem o trabalho: Claude, um modelo de maior raciocínio, cuida do motor e do desenho das telas; um modelo mais simples, rodando no OpenCode Go, implementa a API e as telas. João, o autor, acompanha o núcleo do sistema e aprova os mockups.

Este documento é autocontido. Nenhum agente deve precisar de informação que não esteja aqui ou no repositório. **Precedência:** se algum trecho das seções 2 a 12 conflitar com a seção 1 ou com a seção 8, valem as seções 1 e 8.

### 1.1 O que será entregue

Um app web que recomenda imóveis a partir de escolhas entre pares ("qual você prefere?"). Ele roda inteiro no notebook com Docker Compose, sem internet. São cinco fluxos:

1. **Coleta (`/coleta`):** um colega lê uma tela inicial sobre o experimento, aceita o consentimento, informa a faixa de preço, escolhe uma persona e responde a 20 pares aleatórios de imóveis à venda em Goiânia. O servidor gera o código do participante, e nenhum dado pessoal é coletado. Os dados servem ao experimento.
2. **Onboarding (`/comecar`) e modo demo (`/demo`):** faixa de preço e persona (Família, Investidor ou Estudante), sempre para imóveis à venda em Goiânia. No modo demo, um toque na persona preenche o resto.
3. **Comparações (`/comparar`):** 3 pares na demo, escolhidos pelo motor.
4. **Feed (`/feed`):** o catálogo ordenado por uma nota de afinidade de 0 a 100, com intervalo de incerteza e a alternância Antes e Depois.
5. **Painéis (`/modelo` e `/experimento`):** pesos aprendidos, incerteza e diagnósticos do MCMC, e a acurácia de cada método em pares reais.

O motor é um neurônio sigmoide bayesiano (modelo de Bradley-Terry). Os pesos são amostrados por Metropolis-Hastings escrito à mão em NumPy. A seção 5 especifica o motor, e a seção 5.10 define a interface que o resto do sistema usa.

### 1.2 Prazo

| Data | O que acontece |
| --- | --- |
| qua 04/11 a seg 09/11 | Implementação, conforme a seção 8 |
| qui 05/11, 18h | Link da coleta enviado aos colegas |
| dom 08/11, 12h | Coleta encerrada |
| seg 09/11, 22h | Congelamento do código: tag `v1.0.0`. Depois disso, só correções que impeçam a demo, com autorização de João |
| ter 10/11 | Ensaio, checklist da véspera (seção 10) e estudo. Nenhuma funcionalidade nova |
| qua 11/11 | Apresentação |

Premissa a confirmar (seção 12): João tem de 4 a 5 horas por dia para checkpoints e aprovações. Os agentes trabalham além disso.

### 1.3 Papéis e donos de cada parte

| Papel | Quem | Faz | Não faz |
| --- | --- | --- | --- |
| **A · Arquiteto** | Claude, modelo de maior raciocínio, no Claude Code | Motor completo; catálogo simulado e personas; tema visual, textos e mockups de todas as telas; avaliação e relatório do experimento; revisão do trabalho do executor; checkpoints de entendimento com João | Rotas da API e telas React a partir dos mockups, exceto quando uma tarefa E falhar duas vezes (1.5) |
| **E · Executor** | Modelo mais simples, no OpenCode Go | Repositório, Docker, banco e migração, rotas da API, serviços que chamam o motor pela interface da seção 5.10, telas React a partir dos mockups aprovados, comandos de infraestrutura | Editar arquivos do arquiteto; inventar textos, cores, campos, rotas ou regras que não estejam neste plano |
| **J · Autor e aprovador** | João | Responde aos checkpoints; aprova mockups; envia o link da coleta; decide os cortes | — |

| Caminho | Dono | Os outros podem |
| --- | --- | --- |
| `backend/app/engine/` e `backend/tests/engine/` | A | E só importa (`from app.engine import ...`) e roda os testes |
| `backend/app/seed/` (catálogo, personas, itens de vistoria) | A | E só importa |
| `backend/app/analysis/` | A | E só lê |
| Funções `simulate` e `evaluate` em `backend/app/cli.py` | A | E cria o arquivo e os demais comandos |
| `docs/mockups/`, `frontend/src/styles/theme.css`, `frontend/src/lib/copy.ts` | A | E só lê e importa |
| `docs/PLAN.md` (este documento) | J | Ninguém edita sem pedido de J |
| `docs/CHECKPOINTS.md` | A | J lê; A registra as respostas de J |
| `docs/STATUS.md`, `docs/decisions.md` | A e E | Ambos acrescentam linhas, nunca apagam |
| Todo o resto | E | A revisa e abre tarefas de correção |

O executor cria os arquivos iniciais na tarefa E01. A partir daí, valem os donos desta tabela.

### 1.4 Protocolo do arquiteto: checkpoints de entendimento

João precisa entender o núcleo do sistema a ponto de defendê-lo diante da banca. Por isso, cada parte central termina em um checkpoint. **Claude não faz commit do módulo seguinte do motor antes de o checkpoint anterior estar concluído.** Enquanto espera, pode preparar o próximo módulo sem fazer commit.

Cada checkpoint segue 5 passos:

1. **Explicar** em até 10 frases, em português simples, o que o código faz e por quê, citando a seção correspondente do documento "ImobScore — Bases matemáticas e guia de estudo".
2. **Mostrar** o trecho central do código (até 30 linhas) e rodar no terminal um exemplo numérico com dados do próprio projeto.
3. **Perguntar** a João as 3 perguntas do checkpoint (tabela abaixo), uma de cada vez, e esperar cada resposta. Claude pode trocar uma pergunta por outra do mesmo tipo se o código tiver mudado.
4. **Corrigir** sem dar a resposta antes de João tentar. Se a resposta estiver incompleta, explicar de outro jeito (outro exemplo, um desenho em texto, uma analogia) e perguntar de novo. Responder a todas as dúvidas que João levantar, mesmo fora do roteiro.
5. **Registrar** em `docs/CHECKPOINTS.md`: data, módulo, perguntas, resumo das respostas, dúvidas respondidas e a linha "Entendido: sim". Só João pode declarar "entendido".

| CP | Quando | Módulo | Perguntas (o quê · por quê · e se) | Guia |
| --- | --- | --- | --- | --- |
| CP1 | qua 04/11 | Características e catálogo (A02) | O que o vetor zero representa? · Por que padronizar pela mediana e não pela média? · E se um imóvel tiver 5 quartos, como `bedrooms_sq` muda a utilidade? | 2, 5.4 |
| CP2 | qua 04/11 | Modelo (A03) | O que σ(wᵀd) significa para um par? · Por que o modelo não tem viés? · E se o peso do preço for −3, o que muda na escolha? | 3, 5, 6 |
| CP3 | qui 05/11 | Metropolis-Hastings e diagnósticos (A05) | O que a cadeia guarda a cada passo? · Por que a razão de Hastings não aparece no código? · E se o R-hat der 1,30? | 7 a 9 |
| CP4 | sex 06/11 | Afinidade, BALD e baselines (A06) | O que o score de 87 quer dizer? · Por que a média das sigmoides e não a sigmoide da média? · E se a regressão logística não tivesse regularização? | 6.4, 10 |
| CP5 | sáb 07/11 | Integração motor e API (A-REV2) | O que acontece no servidor quando você responde a um par? · Por que o feed com 0 pares já tem ordem? · E se a persona estiver longe do gosto real? | 7.4, 10 |
| CP6 | dom 08/11 | Experimento real (A08) | O que a curva de acurácia mostra? · Por que os pares da coleta são aleatórios? · E se o MLE ganhar do bayesiano? | 11 |
| CP7 | seg 09/11 | Ensaio de banca (A09) | João explica o motor inteiro em 3 minutos. Claude faz o papel da banca com 5 perguntas da seção 12 do guia | 12 |

### 1.5 Protocolo do executor

O executor é um modelo mais simples e tende a preencher lacunas inventando. As regras abaixo existem para impedir isso.

- Fazer só a tarefa E indicada no pedido, uma por vez, na ordem da seção 8.3.
- Antes de começar, ler o arquivo da tarefa em `docs/tasks/<ID>-*.md` e `docs/STATUS.md`. Esse arquivo é autocontido e é o que vale; o plano só é consultado se faltar algo, lendo apenas a seção necessária.
- Editar apenas os arquivos listados em "Arquivos permitidos" no arquivo da tarefa. Se precisar de outro, parar e registrar o bloqueio em `docs/STATUS.md`.
- Nunca editar arquivos do arquiteto (tabela de 1.3).
- Importar o motor somente por `from app.engine import ...`, com os nomes da seção 5.10.
- Textos de tela vêm de `frontend/src/lib/copy.ts`. Layout, espaçamento e cores vêm do mockup aprovado e de `theme.css`. Nenhum texto visível ao usuário é escrito direto em um componente.
- Nomes de campos, rotas e códigos de erro vêm da seção 6. Não criar campos novos.
- **Se a especificação não responder a uma dúvida, não decidir.** Escrever a pergunta em `docs/STATUS.md`, na parte "Perguntas abertas", e parar a tarefa.
- Não adicionar dependências nem mudar versões além das da seção 2. Não apagar nem afrouxar testes para que passem.
- Terminar só quando todos os comandos de "Verificação" passarem. Registrar o resultado em `docs/STATUS.md` e fazer um commit no formato `tipo(escopo): ID título`, por exemplo `feat(api): E07 rotas da coleta`.
- Se a mesma verificação falhar duas vezes seguidas, parar e marcar a tarefa como "precisa de revisão do arquiteto". Nesse caso, Claude assume a tarefa.

**Pedido padrão para iniciar cada tarefa do executor** (João cola no OpenCode, trocando `{ID}`):

```text
Você é o executor (papel E) do projeto ImobScore.
1. Leia AGENTS.md, docs/STATUS.md e o arquivo da tarefa em docs/tasks/{ID}-*.md. Esse arquivo é autocontido e é o que vale; só consulte docs/PLAN.md se faltar algo, lendo apenas a seção necessária.
2. Implemente somente a tarefa {ID}, editando apenas os "Arquivos permitidos".
3. Se algo não estiver especificado, não invente: escreva a pergunta em docs/STATUS.md ("Perguntas abertas") e pare.
4. Ao terminar, rode todos os comandos de "Verificação" da tarefa, cole o resumo da saída em docs/STATUS.md e faça um commit "tipo(escopo): {ID} título".
```

### 1.6 Mockups e aprovação das telas

Nenhuma tela é implementada antes de João aprovar o mockup dela. O mockup é a fonte da verdade visual: onde a seção 7 e o mockup aprovado divergirem, vale o mockup.

**Formato de cada mockup** (feito por Claude):

- `docs/mockups/<id>-<nome>.html`: HTML estático que abre direto no navegador. Usa Tailwind por CDN (só nos mockups, nunca no app), as mesmas variáveis de cor e fonte de `theme.css` e dados realistas do catálogo simulado. Mostra a tela em celular (375 px) e notebook (1280 px), lado a lado, e todos os estados: normal, carregando, vazio e erro.
- `docs/mockups/<id>-<nome>.md`: a especificação que o executor segue, com estas partes, nesta ordem:

```markdown
# <ID> · <Nome da tela>
Rota: /...   Versão: 1   Status: ver APPROVAL.md
## Objetivo (1 frase)
## Layout (celular e notebook)
## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
## Textos (chaves de copy.ts usadas nesta tela)
## Critérios de aceite visual (lista verificável)
```

**Fluxo de aprovação**

1. Claude abre os HTML no navegador de João e explica, em até 5 frases por tela, as decisões de UX: o que o visitante vê primeiro, o que precisa caber em 60 segundos de demo e como a tela funciona no celular.
2. João responde "aprovado", pede ajustes ou rejeita. Claude ajusta até a aprovação.
3. Claude registra em `docs/mockups/APPROVAL.md` uma linha por tela: `| ID | versão | aprovado | data | observações de João |`.
4. Só a palavra "aprovado" nesse arquivo libera a tarefa E da tela. Mudanças depois disso exigem pedido de João e uma nova versão.

| ID | Tela | Rota | Gate | Prazo de aprovação |
| --- | --- | --- | --- | --- |
| M1 | Coleta: tela inicial, consentimento, faixa de preço, persona e agradecimento | `/coleta` | G1 | qua 04/11, 16h |
| M4 | Comparação de um par (usada na coleta e na demo) | `/comparar` | G1 | qua 04/11, 16h |
| M2 | Início | `/` | G2 | qui 05/11, 18h |
| M3 | Onboarding em dois passos | `/comecar` | G2 | qui 05/11, 18h |
| M3b | Modo demo | `/demo` | G2 | qui 05/11, 18h |
| M5 | Feed com Antes e Depois | `/feed` | G2 | qui 05/11, 18h |
| M6 | Painel do modelo | `/modelo` | G2 | qui 05/11, 18h |
| M7 | Painel do experimento | `/experimento` | G2 | qui 05/11, 18h |
| M8 | Detalhe do imóvel e vistoria | `/imovel/:id` | Só com o corte C1 revertido | seg 09/11, 12h |

### 1.7 Escopo no prazo curto

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

### 1.8 Regras que valem para os dois agentes

- Todo código numérico recebe um `numpy.random.Generator` com semente explícita. Nada usa o estado global de `np.random`.
- Textos da interface em português do Brasil. Nomes de código, tabelas e colunas em inglês.
- Os dados do catálogo são simulados, e a interface diz isso ("catálogo de demonstração").
- Nada depende de internet em execução: sem CDN, sem fontes remotas e sem imagens externas. A única exceção são os mockups em `docs/mockups/`, que não fazem parte do app.
- Claude, ao encontrar uma decisão não prevista, escolhe a opção mais simples compatível com o plano e registra uma linha em `docs/decisions.md`. O executor não decide: pergunta (1.5).
- Ao fim de cada tarefa, o dono atualiza `docs/STATUS.md`.

## 2. Stack e decisões

O back-end é Python com FastAPI e PostgreSQL. O front-end é React com Vite, tudo em TypeScript. As versões abaixo são a linha mínima: o agente instala a última versão estável de cada uma, fixa a versão nos lockfiles (`uv.lock`, `pnpm-lock.yaml`) e anota em `docs/decisions.md` se alguma linha mudou de versão principal.

### Back-end

| Ferramenta | Versão | Para quê |
| --- | --- | --- |
| Python | 3.12 | Linguagem do back-end e do motor |
| uv | atual | Gerenciador de pacotes e ambientes, com lockfile reprodutível |
| FastAPI | atual | API HTTP com OpenAPI gerado automaticamente |
| Uvicorn | atual | Servidor ASGI |
| Pydantic v2 + pydantic-settings | 2.x | Schemas da API e configuração por variáveis de ambiente |
| SQLAlchemy | 2.0 | ORM no estilo 2.0 (`Mapped[...]`), com sessões síncronas |
| psycopg | 3.x | Driver do PostgreSQL |
| Alembic | 1.x | Migrações do banco |
| PostgreSQL | 17 | Banco de dados, via imagem `postgres:17-alpine` |
| NumPy | 2.x | Motor: verossimilhança, Metropolis-Hastings e afinidade |
| scikit-learn | 1.x | Só o baseline de máxima verossimilhança (`LogisticRegression`) |
| SciPy | 1.x | Só nos testes (otimizador para conferir o MAP) |
| Faker (pt\_BR) | atual | \[não usar\] O catálogo usa listas fixas de bairros (tarefa A02), para ser determinístico entre versões |
| Matplotlib | 3.x | Figuras do relatório, geradas pelo script de avaliação |
| Typer | atual | Comandos de linha (`seed`, `evaluate`, `export`) |
| pytest + pytest-cov + httpx | atual | Testes unitários e de API |
| Ruff | atual | Lint e formatação |
| mypy (modo `strict` em `app/engine`) | atual | Checagem de tipos |

O banco usa sessões síncronas, porque o motor é CPU puro e o MVP tem poucos usuários. Async não traria ganho e complicaria os testes. As rotas que rodam o MCMC são `def`, e não `async def`, para o FastAPI rodá-las no pool de threads.

### Front-end

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

### Infra e ferramentas gerais

| Ferramenta | Para quê |
| --- | --- |
| Docker + Docker Compose | Serviços `db`, `api` e `web` rodando localmente e offline |
| Nginx (imagem `nginx:alpine`) | Serve o build do front-end e faz proxy de `/api` para a API |
| Makefile | Atalhos: `make up`, `make seed`, `make test`, `make demo`, `make evaluate` |
| pre-commit | \[corte\] Substituído pelo comando make check (seção 9) |
| GitHub Actions | \[corte\] Substituído pelo comando make check (seção 9) |
| Cloudflare Tunnel (`cloudflared`, opcional) | Expor a página de coleta aos colegas a partir do notebook, sem deploy (ver seção 12) |

### Decisões já tomadas

- **Sem login no MVP.** Cada pessoa recebe uma sessão anônima com UUID v4, criada no onboarding e guardada no navegador. Autenticação fica para a fase 2.
- **Monorepo** com `backend/` e `frontend/` no mesmo repositório.
- **Metropolis-Hastings em NumPy**, com cadeias vetorizadas (as 16 cadeias avançam juntas em um array).
- **Catálogo simulado e determinístico:** mesma semente, mesmo catálogo.
- **Sem fotos externas.** Cada cartão usa uma ilustração SVG local por tipo de imóvel (ver seção 12).

## 3. Arquitetura e estrutura do repositório

São três serviços no Docker Compose. O motor é uma biblioteca Python pura: recebe arrays NumPy e devolve arrays, sem banco e sem HTTP. Isso permite testar o motor isolado e reutilizá-lo no script de avaliação.

&#91;embedded content: arquitetura · 3 serviços do Docker Compose + CLI\]

O navegador fala só com o Nginx. O Nginx repassa `/api` para a API, e a API é a única que acessa o banco e chama o motor.

### Camadas do back-end

- `api/` (rotas): valida a entrada com Pydantic, chama um serviço e devolve um schema. Não contém regra de negócio.
- `services/`: busca dados no banco, monta as matrizes, chama o motor e grava o resultado. Toda transação abre e fecha aqui.
- `engine/`: só matemática. Nenhum import de SQLAlchemy, FastAPI ou Pydantic. O mypy roda em modo `strict` nesta pasta.
- `models/`: tabelas do SQLAlchemy. `schemas/`: modelos Pydantic de entrada e saída.

### Estrutura de pastas

```text
imobscore/
├── docker-compose.yml
├── .env.example
├── Makefile
├── AGENTS.md                # instruções do executor (OpenCode)
├── CLAUDE.md                # instruções do arquiteto (Claude Code)
├── docs/
│   ├── PLAN.md              # este documento
│   ├── decisions.md         # decisões não previstas, uma por linha
│   ├── STATUS.md            # andamento, perguntas abertas e bloqueios
│   ├── CHECKPOINTS.md       # checkpoints de entendimento (1.4)
│   ├── results.md           # resultado do experimento (A08)
│   ├── demo-script.md       # roteiro da demo (A09)
│   └── mockups/             # M1..M8 (.html e .md) e APPROVAL.md
├── data/
│   ├── collected/           # pares exportados em JSON (vai para o Git)
│   └── results/             # métricas e figuras do experimento
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── migrations/
│   ├── app/
│   │   ├── main.py           # cria o FastAPI, CORS, routers
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── db.py             # engine e SessionLocal
│   │   ├── deps.py           # get_db, get_session_or_404
│   │   ├── api/v1/           # meta.py sessions.py feed.py listings.py experiment.py
│   │   ├── models/           # listing.py persona.py session.py comparison.py ...
│   │   ├── schemas/
│   │   ├── services/         # session_service.py pair_service.py feed_service.py ...
│   │   ├── analysis/
│   │   │   └── report.py     # summary.csv e figuras do experimento (A07)
│   │   ├── engine/
│   │   │   ├── __init__.py   # interface pública do motor (seção 5.10)
│   │   │   ├── features.py   # especificação e transformação das 12 características
│   │   │   ├── model.py      # sigmoide, log-verossimilhança, log-priori, log-posteriori
│   │   │   ├── mcmc.py       # Metropolis-Hastings vetorizado
│   │   │   ├── diagnostics.py# R-hat, ESS, taxa de aceitação
│   │   │   ├── affinity.py   # afinidade, intervalo e explicação
│   │   │   ├── pairs.py      # escolha do próximo par
│   │   │   ├── baselines.py  # pesos iguais, persona, máxima verossimilhança
│   │   │   └── evaluation.py # protocolo de avaliação e simulação (5.9)
│   │   ├── seed/
│   │   │   ├── personas.yaml
│   │   │   ├── inspection_items.yaml
│   │   │   └── catalog.py    # gerador do catálogo simulado
│   │   └── cli.py            # Typer: seed, evaluate, export, simulate
│   └── tests/
│       ├── engine/
│       ├── services/
│       └── api/
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

## 4. Modelo de dados (PostgreSQL)

São 8 tabelas, criadas por uma única migração inicial do Alembic. O DDL abaixo é a referência: o agente escreve os modelos do SQLAlchemy 2.0 que geram exatamente este esquema e confere com `alembic upgrade head` seguido de `\d+` no `psql`.

| Tabela | Guarda | Escrita por |
| --- | --- | --- |
| `listings` | Os \~300 imóveis simulados e seus atributos brutos | Comando `seed` |
| `feature_stats` | Centro (mediana) e escala de cada característica, por cidade e finalidade | Comando `seed` |
| `personas` | Família, Investidor e Estudante, com média e desvio da priori | Comando `seed` (de `personas.yaml`) |
| `sessions` | Uma pessoa: respostas do onboarding, persona e modo | `POST /sessions` |
| `comparisons` | Cada par mostrado e a escolha feita | Fluxo de comparações |
| `posteriors` | Amostras do MCMC e resumo, por sessão e por número de pares | Serviço do motor |
| `inspections` | Ajustes da vistoria (Δ de −10 a +10) por sessão e imóvel | Tela de detalhe |
| `experiment_results` | Métricas de cada método por participante e tamanho de treino | Comando `evaluate` |

```sql
CREATE TABLE listings (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text UNIQUE NOT NULL,              -- ex.: GYN-V-0042
  city            text NOT NULL,                     -- só 'Goiânia' no MVP
  purpose         text NOT NULL CHECK (purpose IN ('sale','rent')),
  kind            text NOT NULL CHECK (kind IN ('apartment','house')),
  title           text NOT NULL,
  neighborhood    text NOT NULL,
  price_brl       numeric(12,2) NOT NULL CHECK (price_brl > 0), -- só venda no MVP
  area_m2         numeric(7,1)  NOT NULL CHECK (area_m2 > 0),
  bedrooms        smallint NOT NULL CHECK (bedrooms BETWEEN 1 AND 6),
  bathrooms       smallint NOT NULL CHECK (bathrooms BETWEEN 1 AND 6),
  parking         smallint NOT NULL CHECK (parking BETWEEN 0 AND 4),
  dist_center_km  numeric(5,2) NOT NULL CHECK (dist_center_km >= 0),
  age_years       smallint NOT NULL CHECK (age_years BETWEEN 0 AND 60),
  leisure_count   smallint NOT NULL CHECK (leisure_count BETWEEN 0 AND 3), -- piscina, academia, salão
  pet_friendly    boolean NOT NULL,
  doorman_24h     boolean NOT NULL,
  illustration    text NOT NULL,                     -- chave do SVG local
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_listings_segment ON listings (city, purpose, price_brl);

CREATE TABLE feature_stats (
  city        text NOT NULL,
  purpose     text NOT NULL,
  feature_key text NOT NULL,
  center      double precision NOT NULL,             -- mediana no segmento
  scale       double precision NOT NULL CHECK (scale > 0), -- IQR / 1.349
  PRIMARY KEY (city, purpose, feature_key)
);

CREATE TABLE personas (
  slug            text PRIMARY KEY,                  -- 'familia' | 'investidor' | 'estudante'
  name            text NOT NULL,
  description     text NOT NULL,
  prior_mean      jsonb NOT NULL,                    -- {feature_key: float}, 12 chaves
  prior_sd        jsonb NOT NULL,                    -- {feature_key: float > 0}
  demo_defaults   jsonb NOT NULL                     -- cidade, finalidade e faixa para o modo demo
);

CREATE TABLE sessions (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mode             text NOT NULL CHECK (mode IN ('product','demo','collection')),
  city             text NOT NULL,
  purpose          text NOT NULL CHECK (purpose IN ('sale','rent')),
  price_min        numeric(12,2) NOT NULL,
  price_max        numeric(12,2) NOT NULL,
  persona_slug     text NOT NULL REFERENCES personas(slug),
  target_pairs     smallint NOT NULL,                 -- demo 3, produto 8, coleta 25
  participant_code text,                             -- só na coleta: gerado pelo servidor (P01, P02...)
  consent_at       timestamptz,                      -- obrigatório quando mode = 'collection'
  status           text NOT NULL DEFAULT 'comparing' CHECK (status IN ('comparing','done')),
  created_at       timestamptz NOT NULL DEFAULT now(),
  CHECK (price_min < price_max),
  CHECK (mode <> 'collection' OR (participant_code IS NOT NULL AND consent_at IS NOT NULL))
);

CREATE TABLE comparisons (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id    uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  position      smallint NOT NULL,                   -- 1, 2, 3...
  listing_a_id  uuid NOT NULL REFERENCES listings(id), -- mostrado à esquerda
  listing_b_id  uuid NOT NULL REFERENCES listings(id), -- mostrado à direita
  selection     text NOT NULL CHECK (selection IN ('adaptive','random')),
  chosen        char(1) CHECK (chosen IN ('A','B')),  -- NULL enquanto não respondido
  shown_at      timestamptz NOT NULL DEFAULT now(),
  answered_at   timestamptz,
  response_ms   integer,
  UNIQUE (session_id, position),
  CHECK (listing_a_id <> listing_b_id)
);

CREATE TABLE posteriors (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id     uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  n_comparisons  smallint NOT NULL,
  seed           bigint NOT NULL,
  samples        bytea NOT NULL,                     -- np.save de float32 [4000, 12]
  mean           jsonb NOT NULL,
  sd             jsonb NOT NULL,
  ci_low         jsonb NOT NULL,                     -- percentil 5
  ci_high        jsonb NOT NULL,                     -- percentil 95
  accept_rate    double precision NOT NULL,
  rhat_max       double precision NOT NULL,
  ess_min        double precision NOT NULL,
  step_size      double precision NOT NULL,
  elapsed_ms     integer NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (session_id, n_comparisons)
);

CREATE TABLE inspections (
  session_id  uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  listing_id  uuid NOT NULL REFERENCES listings(id),
  item_key    text NOT NULL,                         -- chave de inspection_items.yaml
  delta       smallint NOT NULL CHECK (delta BETWEEN -10 AND 10),
  created_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (session_id, listing_id, item_key)
);

CREATE TABLE experiment_results (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id           uuid NOT NULL,
  participant_code text NOT NULL,
  method           text NOT NULL CHECK (method IN ('equal','persona','mle','bayes')),
  n_train          smallint NOT NULL,                -- 3, 5, 10
  split_seed       integer NOT NULL,
  n_test           smallint NOT NULL,
  accuracy         double precision NOT NULL,
  log_loss         double precision NOT NULL,
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_results_run ON experiment_results (run_id, method, n_train);
```

**Regras do banco**

- As características transformadas e padronizadas não são guardadas. Elas são recalculadas em memória a partir de `listings` e `feature_stats`, porque são baratas e assim a fórmula fica em um só lugar (`engine/features.py`).
- `posteriors.samples` guarda as amostras em `float32` (cerca de 4.000 × 12 × 4 bytes = 192 kB por linha). O feed reaproveita a última posteriori em vez de rodar o MCMC de novo.
- `comparisons.chosen` fica nulo entre mostrar o par e receber a resposta, o que permite retomar a sessão após recarregar a página.
- A convenção de nomes do SQLAlchemy (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) é definida no `MetaData` antes da primeira migração.

## 5. Especificação do motor

O motor transforma cada imóvel em um vetor z de 12 números, aprende um vetor de pesos w por pessoa e dá a cada imóvel a probabilidade de ser preferido a um imóvel típico. Todo o código fica em `backend/app/engine/`, recebe e devolve `np.ndarray` com `dtype=float64` e não faz I/O.

### 5.1 Características (`features.py`)

A tabela abaixo é a proposta inicial das 12 características, ainda pendente de confirmação do autor (seção 12). Ela fica em uma lista de `FeatureSpec` imutáveis. A coluna "Direção" só é usada pelo baseline de pesos iguais.

| # | Chave | Transformação t(x) | Direção | Texto quando acima / abaixo do típico |
| --- | --- | --- | --- | --- |
| 1 | `log_price` | ln(price\_brl) | −1 | mais caro / mais barato que o típico |
| 2 | `log_area` | ln(area\_m2) | +1 | mais espaçoso / mais compacto |
| 3 | `bedrooms` | bedrooms | +1 | mais quartos / menos quartos |
| 4 | `bedrooms_sq` | (bedrooms − 3)² | −1 | longe de 3 quartos / perto de 3 quartos |
| 5 | `bathrooms` | bathrooms | +1 | mais banheiros / menos banheiros |
| 6 | `parking` | parking | +1 | mais vagas / menos vagas |
| 7 | `dist_center` | dist\_center\_km | −1 | longe do centro / perto do centro |
| 8 | `age` | age\_years | −1 | mais antigo / mais novo |
| 9 | `is_house` | 1 se casa, 0 se apartamento | 0 | é casa / é apartamento |
| 10 | `leisure` | leisure\_count (0 a 3) | +1 | mais lazer / menos lazer |
| 11 | `pet` | 1 se aceita pet | +1 | aceita pet / não aceita pet |
| 12 | `doorman` | 1 se portaria 24 h | +1 | tem portaria 24 h / sem portaria |

A característica 4 existe para capturar preferências com pico. Com peso positivo em `bedrooms` e negativo em `bedrooms_sq`, a utilidade sobe até um número de quartos e depois cai.

**Padronização.** Para cada segmento (cidade, finalidade) e cada característica j, o comando `seed` calcula o centro e a escala sobre todos os imóveis do segmento e grava em `feature_stats`:

```latex
c_j = \operatorname{mediana}(t_j), \qquad s_j = \frac{\operatorname{IQR}(t_j)}{1{,}349}, \qquad z_j(x) = \frac{t_j(x) - c_j}{s_j}
```

Se o IQR for zero, usar o desvio padrão. Se ele também for zero, usar 1. Como o centro é a mediana, o "imóvel típico" vira o vetor zero no espaço padronizado.

```python
@dataclass(frozen=True)
class FeatureSpec:
    key: str
    label: str          # rótulo em pt-BR para a interface
    direction: int      # -1, 0 ou +1 (só baseline de pesos iguais)
    text_high: str
    text_low: str

FEATURES: tuple[FeatureSpec, ...]  # 12 itens, nesta ordem
def raw_matrix(rows: Sequence[ListingRow]) -> np.ndarray: ...            # (n, 12), t(x)
def standardize(T: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray: ...  # (n, 12), z
def fit_stats(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...       # (center, scale)
```

### 5.2 Modelo (`model.py`)

Para cada par respondido i, o vetor de diferença é sempre orientado do vencedor para o perdedor. Assim todos os rótulos são 1:

```latex
d_i = z(\text{vencedor}_i) - z(\text{perdedor}_i), \qquad P(\text{vencedor} \succ \text{perdedor} \mid w) = \sigma(w^\top d_i), \qquad \sigma(u) = \frac{1}{1 + e^{-u}}
```

```latex
\log p(w \mid D) = \underbrace{-\sum_{i=1}^{m} \log\left(1 + e^{-w^\top d_i}\right)}_{\text{log-verossimilhança}} \; \underbrace{- \frac{1}{2}\sum_{j=1}^{12} \left(\frac{w_j - \mu_j}{\sigma_j}\right)^2}_{\text{log-priori}} + \text{const}
```

Na implementação, log(1 + e^(−u)) é `np.logaddexp(0.0, -u)`, para não estourar com |u| grande. A função aceita `w` com forma (C, 12) e devolve (C,), para avaliar as C cadeias de uma vez.

```python
def sigmoid(u: np.ndarray) -> np.ndarray: ...   # estável: usa np.exp(-np.logaddexp(0, -u))
def log_likelihood(W: np.ndarray, D: np.ndarray) -> np.ndarray: ...  # W (C,12), D (m,12) -> (C,)
def log_prior(W: np.ndarray, mu: np.ndarray, sd: np.ndarray) -> np.ndarray: ...
def log_posterior(W, D, mu, sd) -> np.ndarray: ...  # soma das duas; com m = 0 é só a priori
```

### 5.3 Priori das personas (`seed/personas.yaml`)

Cada persona define a média μ da priori, na escala padronizada (efeito de uma escala robusta s\_j no log da chance). O desvio da priori é σ\_j = 1,0 para todas as características, configurável por `PRIOR_SD`. Os valores abaixo são um ponto de partida plausível, para o autor revisar.

| Chave | Família | Investidor | Estudante |
| --- | --- | --- | --- |
| `log_price` | −1,0 | −1,5 | −2,0 |
| `log_area` | 0,8 | 0,3 | 0,2 |
| `bedrooms` | 0,6 | 0,2 | −0,2 |
| `bedrooms_sq` | −0,4 | −0,2 | −0,3 |
| `bathrooms` | 0,4 | 0,2 | 0,1 |
| `parking` | 0,5 | 0,2 | 0,0 |
| `dist_center` | −0,3 | −0,8 | −1,2 |
| `age` | −0,3 | −0,5 | −0,1 |
| `is_house` | 0,5 | −0,2 | −0,3 |
| `leisure` | 0,4 | 0,3 | 0,2 |
| `pet` | 0,3 | 0,0 | 0,2 |
| `doorman` | 0,4 | 0,4 | 0,1 |

Cada persona também tem `demo_defaults` para o modo demo: Família = Goiânia, compra, R$ 350 mil a R$ 900 mil; Investidor = Goiânia, compra, R$ 200 mil a R$ 600 mil; Estudante = Goiânia, compra, R$ 150 mil a R$ 350 mil.

### 5.4 Metropolis-Hastings (`mcmc.py`)

Passeio aleatório gaussiano com as 16 cadeias avançando juntas. A adaptação do passo acontece só no aquecimento. Depois dele o passo fica fixo, o que mantém a cadeia válida.

| Parâmetro | Valor padrão | Variável de ambiente |
| --- | --- | --- |
| Cadeias C | 16 (vetorizadas, quase o custo de uma) | `MCMC_CHAINS` |
| Iterações de aquecimento por cadeia | 1.000 | `MCMC_WARMUP` |
| Iterações após o aquecimento por cadeia | 2.000 | `MCMC_DRAWS` |
| Desbaste (guardar 1 a cada k) | 8, ou seja, 250 por cadeia e S = 4.000 no total | `MCMC_THIN` |
| Passo inicial h | 2,38 / √12 ≈ 0,687 | — |
| Taxa de aceitação alvo | 0,30 | — |
| Janela de adaptação | 50 iterações | — |

Por que 16 cadeias: um passeio aleatório em 12 dimensões rende cerca de 2% de amostras efetivas. Em um teste com 40 pares, 4 cadeias × 1.000 amostras deram ESS mínimo de \~70, e 16 cadeias × 2.000 deram \~450, em cerca de 190 ms. Como as cadeias avançam juntas em um array, quadruplicar as cadeias quase não muda o tempo.

Algoritmo, exatamente nesta ordem:

1. `rng = np.random.default_rng(seed)`. A semente é o inteiro formado pelos 8 primeiros bytes de `sha256(f"{session_id}:{n_comparisons}")`, e fica gravada em `posteriors.seed`.
2. Ponto inicial de cada cadeia: `W = mu + sd * rng.standard_normal((C, 12))`. As cadeias começam espalhadas, o que é necessário para o R-hat funcionar.
3. `lp = log_posterior(W)`.
4. Para cada iteração t = 1 … WARMUP + DRAWS:
   1. Proposta: `W_prop = W + h * sd * rng.standard_normal((C, 12))`.
   2. `lp_prop = log_posterior(W_prop)`.
   3. Aceita onde `np.log(rng.random(C)) < lp_prop - lp`. Nessas cadeias, `W` e `lp` recebem os valores propostos.
   4. Se t ≤ WARMUP e t é múltiplo de 50: com `a` = taxa de aceitação média da janela, faça `h = h * exp(a - 0.30)`, limitado a \[0,01; 5\].
   5. Se t > WARMUP e (t − WARMUP) é múltiplo de THIN, guarde `W` na próxima posição de `samples[:, k, :]`.
5. Devolva `MCMCResult(samples=(C, DRAWS // THIN, 12), accept_rate=<aceitação após o aquecimento>, step_size=h, seed=seed)`.

A proposta é simétrica, então a razão de Hastings se cancela e não aparece no código. Escreva isso em um comentário no código. Meta de desempenho: até 250 ms com 40 pares no notebook.

### 5.5 Diagnósticos (`diagnostics.py`)

- **R-hat dividido:** corte cada cadeia guardada ao meio (32 meias-cadeias de n = 125). Com B = variância entre as médias das meias-cadeias vezes n e W = média das variâncias dentro delas, calcule `rhat = sqrt(((n - 1) / n * W + B / n) / W)` para cada peso.
- **ESS:** autocorrelação média entre as cadeias, somada até a primeira soma de pares consecutivos negativa (Geyer). `ess = S / (1 + 2 * soma)`.
- **Critério:** `rhat_max < 1.05`, `ess_min > 400` e aceitação entre 0,15 e 0,50. Se falhar, rode de novo uma vez com aquecimento e amostras dobrados. Se falhar de novo, grave assim mesmo, registre um aviso no log e devolva `diagnostics.ok = false` na API. Isso não bloqueia o fluxo.

### 5.6 Afinidade, score e explicação (`affinity.py`)

Com as S = 4.000 amostras guardadas w\_s achatadas em (S, 12) e Z com forma (n, 12):

```latex
a_s(x) = \sigma\left(w_s^\top z(x)\right), \qquad \text{afinidade}(x) = \frac{1}{S}\sum_{s=1}^{S} a_s(x), \qquad \text{score}(x) = \operatorname{clip}\left(\operatorname{round}(100 \cdot \text{afinidade}(x)) + \sum \Delta_{\text{vistoria}},\; 0,\; 100\right)
```

- O intervalo exibido é formado pelos percentis 5 e 95 de a\_s(x), multiplicados por 100.
- O selo diz: "{score}% de chance de você preferir este a um imóvel típico".
- **Explicação:** a contribuição de cada característica é c\_j = w̄\_j · z\_j(x), em que w̄ é a média das amostras. Mostre as 3 maiores contribuições positivas e a mais negativa, usando `text_high` se z\_j > 0 e `text_low` se z\_j < 0. Ignore |c\_j| < 0,1.
- Calcule tudo em lote: `sigmoid(Z @ samples.T)` tem forma (n, S). Para 300 imóveis e 4.000 amostras, isso cabe folgado na memória.

### 5.7 Escolha do próximo par (`pairs.py`)

- **Candidatos:** imóveis do segmento da sessão com preço entre 0,85 × `price_min` e 1,15 × `price_max`. Se forem menos de 20, use o segmento inteiro.
- **Modo `collection` (coleta):** pares sorteados ao acaso (`selection = 'random'`), sem repetir par e com cada imóvel aparecendo no máximo 3 vezes. A coleta não roda MCMC entre os pares. Os pares precisam ser aleatórios para que a avaliação não dependa de nenhum dos modelos comparados.
- **Modos `product` e `demo`:** escolha adaptativa (`selection = 'adaptive'`). Sorteie K = 300 pares candidatos ainda não mostrados e escolha o de maior informação esperada (BALD). Antes do primeiro par, use 4.000 amostras sorteadas direto da priori.

```latex
p_s = \sigma\left(w_s^\top (z_A - z_B)\right), \quad \bar p = \frac{1}{S}\sum_s p_s, \quad H(p) = -p\log p - (1-p)\log(1-p), \quad \text{BALD} = H(\bar p) - \frac{1}{S}\sum_s H(p_s)
```

- Sorteie qual imóvel vai à esquerda, para não haver viés de posição. O da esquerda é sempre `listing_a`.
- No modo demo, o MCMC roda depois de cada resposta, porque o próximo par depende da posteriori atual.

### 5.8 Baselines (`baselines.py`)

| Método (`method`) | Pesos | Probabilidade de A ≻ B |
| --- | --- | --- |
| `equal` (pesos iguais) | w = vetor de direções da tabela 5.1 | σ(wᵀ(z\_A − z\_B)) |
| `persona` (média ponderada da persona) | w = μ da persona, sem aprendizado | σ(wᵀ(z\_A − z\_B)) |
| `mle` (máxima verossimilhança) | `LogisticRegression(fit_intercept=False, C=1.0)` treinada com os pares duplicados de forma simétrica: (d\_i, 1) e (−d\_i, 0) | `predict_proba` em z\_A − z\_B |
| `bayes` (motor) | Amostras do MCMC | média de σ(w\_sᵀ(z\_A − z\_B)) sobre as amostras |

A duplicação simétrica é necessária porque, com todos os rótulos iguais a 1, o scikit-learn recusa o treino por ter uma só classe. O `C=1.0` é a regularização L2 padrão do scikit-learn. Sem ela, com 3 pares os pesos vão para o infinito. O relatório deve dizer isso.

No feed, a comparação lado a lado usa `persona` à esquerda e `bayes` à direita, com o mesmo cálculo de afinidade da seção 5.6 (para `persona`, S = 1 e w = μ).

### 5.9 Protocolo de avaliação (comando `evaluate`)

1. Entram as sessões `collection` com pelo menos 20 pares respondidos e mediana de `response_ms` de pelo menos 1.000 ms. Os pares também são exportados para `data/collected/pairs.json` pelo comando `export`, e o `evaluate` aceita esse arquivo como entrada (`--from-json`). Assim a avaliação roda sem banco.
2. Para cada participante, cada n\_train em {3, 5, 10} e cada `split_seed` de 0 a 19: sorteie 10 pares de teste. Os pares de treino são os n\_train primeiros dos que sobraram, em ordem embaralhada.
3. Treine `mle` e `bayes` só com o treino. `equal` e `persona` não treinam, mas são avaliados nos mesmos pares de teste.
4. Métricas no teste: **acurácia** (acerto quando p > 0,5; p = 0,5 vale meio acerto) e **perda logarítmica** (com p limitado a \[10⁻⁶, 1 − 10⁻⁶\]).
5. Grave uma linha por (participante, método, n\_train, split) em `experiment_results`, todas com o mesmo `run_id`.
6. Gere `data/results/summary.csv` com média e desvio padrão sobre os splits, e duas figuras em PNG: `accuracy_vs_ntrain.png` (uma linha por método, com faixa de ±1 desvio) e `accuracy_by_participant.png` (n\_train = 5, barras por participante e método).

O comando `simulate` cria participantes sintéticos (`participant_code` S01, S02…) com w verdadeiro = μ da persona + ruído N(0; 0,7²) e escolhas sorteadas pelo próprio modelo. Ele serve para testar o pipeline e como plano B se os colegas não responderem. Resultados simulados são sempre rotulados como simulados na interface e no relatório.

### 5.10 Interface pública do motor (`engine/__init__.py`)

O executor só enxerga o motor por estes nomes. Claude implementa todos eles e não muda nenhuma assinatura sem atualizar esta seção e avisar João na mesma alteração. Todos os arrays são `np.ndarray` de `float64`, e "12" é sempre o número de características, na ordem de `FEATURE_KEYS`.

```python
# backend/app/engine/__init__.py
from app.engine.features import (
    FEATURES, FEATURE_KEYS, FeatureSpec, ListingLike, raw_matrix, fit_stats, standardize,
)
from app.engine.mcmc import MCMCConfig, MCMCResult, fit_posterior
from app.engine.diagnostics import Diagnostics, is_ok
from app.engine.affinity import AffinityResult, Reason, compute_affinity, to_score, explain
from app.engine.pairs import seed_for, random_pairs, next_pair_bald
from app.engine.baselines import Method, fit_mle, predict_proba
from app.engine.evaluation import ResultRow, evaluate_participant, simulate_choices
```

```python
# ---------- features.py ----------
FEATURE_KEYS: tuple[str, ...]          # as 12 chaves da tabela 5.1, nesta ordem
FEATURES: tuple[FeatureSpec, ...]      # mesma ordem

class ListingLike(Protocol):           # serve para a linha do ORM e para ListingRow do catálogo
    price_brl: Decimal | float; area_m2: Decimal | float; bedrooms: int; bathrooms: int
    parking: int; dist_center_km: Decimal | float; age_years: int; kind: str
    leisure_count: int; pet_friendly: bool; doorman_24h: bool

def raw_matrix(rows: Sequence[ListingLike]) -> np.ndarray: ...            # (n, 12) = t(x), antes da padronização
def fit_stats(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...       # (center (12,), scale (12,))
def standardize(T: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray: ...  # (n, 12) = z

# ---------- mcmc.py ----------
@dataclass(frozen=True)
class MCMCConfig:
    chains: int = 16; warmup: int = 1000; draws: int = 2000; thin: int = 8; target_accept: float = 0.30

@dataclass(frozen=True)
class MCMCResult:
    samples: np.ndarray        # (S, 12), S = chains * draws // thin = 4000, em ordem por cadeia:
                               # linhas [k*K:(k+1)*K] são a cadeia k, com K = draws // thin
    n_chains: int
    seed: int
    diagnostics: Diagnostics

def fit_posterior(D: np.ndarray, mu: np.ndarray, sd: np.ndarray, seed: int,
                  cfg: MCMCConfig = MCMCConfig()) -> MCMCResult: ...
# D: (m, 12), cada linha = z(vencedor) - z(perdedor). m pode ser 0.
# m = 0: devolve S amostras sorteadas direto de N(mu, sd^2), com diagnostics
#        accept_rate=1.0, rhat_max=1.0, ess_min=S, step_size=0.0, ok=True.
# m > 0: Metropolis-Hastings da seção 5.4, com a regra de nova tentativa da seção 5.5.

# ---------- diagnostics.py ----------
@dataclass(frozen=True)
class Diagnostics:
    accept_rate: float; rhat_max: float; ess_min: float
    step_size: float; elapsed_ms: int; ok: bool   # mesmos nomes do schema Diagnostics da seção 6
def is_ok(accept_rate: float, rhat_max: float, ess_min: float) -> bool: ...
# critério da seção 5.5; `posteriors` não guarda `ok`, então o serviço recalcula ao carregar a linha

# ---------- affinity.py ----------
@dataclass(frozen=True)
class AffinityResult:
    mean: np.ndarray; p5: np.ndarray; p95: np.ndarray   # cada um (n,), valores em [0, 1]

@dataclass(frozen=True)
class Reason:
    feature_key: str; text: str; contribution: float

def compute_affinity(Z: np.ndarray, samples: np.ndarray) -> AffinityResult: ...
# Z (n, 12), samples (S, 12). Para o método "persona": samples = mu[None, :] (S = 1).
def to_score(affinity: float, inspection_delta: int = 0) -> int: ...
# clip(round(100 * affinity) + inspection_delta, 0, 100)
def explain(z: np.ndarray, w_mean: np.ndarray, max_reasons: int = 4) -> list[Reason]: ...
# regra da seção 5.6; z (12,), w_mean (12,)

# ---------- pairs.py ----------
def seed_for(session_id: UUID | str, n: int) -> int: ...
# int.from_bytes(sha256(f"{session_id}:{n}".encode()).digest()[:8], "big")
def random_pairs(n_items: int, n_pairs: int, rng: np.random.Generator,
                 max_appearances: int = 3) -> list[tuple[int, int]]: ...
# índices (esquerda, direita) em 0..n_items-1; sem repetir par; cada índice no máximo
# max_appearances vezes; lado sorteado. ValueError se for impossível.
def next_pair_bald(Z: np.ndarray, samples: np.ndarray, shown: set[frozenset[int]],
                   rng: np.random.Generator, k: int = 300) -> tuple[int, int]: ...
# seção 5.7; devolve (esquerda, direita) em índices de Z; nunca um par de shown.
# Se o corte C3 for aplicado, o serviço usa random_pairs no lugar desta função.

# ---------- baselines.py ----------
Method = Literal["equal", "persona", "mle", "bayes"]
def fit_mle(D: np.ndarray) -> np.ndarray: ...           # (12,), seção 5.8
def predict_proba(method: Method, D: np.ndarray, *, mu: np.ndarray | None = None,
                  samples: np.ndarray | None = None, w_mle: np.ndarray | None = None) -> np.ndarray: ...
# (m,) = probabilidade de o primeiro imóvel de cada linha de D vencer

# ---------- evaluation.py ----------
@dataclass(frozen=True)
class ResultRow:
    participant_code: str; method: Method; n_train: int; split_seed: int
    n_test: int; accuracy: float; log_loss: float

def evaluate_participant(code: str, D: np.ndarray, mu: np.ndarray, sd: np.ndarray, *,
                         n_train_list: tuple[int, ...] = (3, 5, 10), n_splits: int = 20,
                         n_test: int = 10, cfg: MCMCConfig = MCMCConfig()) -> list[ResultRow]: ...
# D (m, 12) = pares do participante, orientados vencedor - perdedor, na ordem respondida; protocolo 5.9
def simulate_choices(D_left_minus_right: np.ndarray, w_true: np.ndarray,
                     rng: np.random.Generator) -> np.ndarray: ...
# (m,) de "A" ou "B", sorteados com P(A) = sigma(w_true . d)
```

## 6. API (FastAPI)

Todas as rotas ficam sob `/api/v1`, devolvem JSON em `snake_case` e têm `response_model` declarado, para que o OpenAPI gere os tipos do front-end. A sessão anônima é identificada pelo UUID no caminho.

| Método e rota | Faz | Resposta |
| --- | --- | --- |
| `GET /health` | Verifica a API e o banco (`SELECT 1`) | `{status, db}` |
| `GET /meta/options` | Cidades, finalidades e faixa de preço mínima e máxima por segmento | `MetaOptions` |
| `GET /meta/personas` | As 3 personas, com nome, descrição e `demo_defaults` | `list[PersonaOut]` |
| `GET /meta/features` | As 12 características, com chave, rótulo e textos | `list[FeatureOut]` |
| `GET /meta/inspection-items` | Itens da vistoria com Δ sugerido | `list[InspectionItemOut]` |
| `POST /sessions` | Cria a sessão a partir do onboarding | `201 SessionOut` |
| `GET /sessions/{id}` | Estado da sessão e progresso | `SessionOut` |
| `GET /sessions/{id}/next-pair` | Devolve o par pendente ou cria o próximo. Retorna `204` quando `target_pairs` foi atingido | `PairOut` |
| `POST /sessions/{id}/comparisons/{position}` | Registra a escolha. Fora do modo coleta, recalcula a posteriori | `AnswerOut` |
| `GET /sessions/{id}/feed` | Feed paginado, com `method=bayes` (padrão) ou `method=persona` | `FeedPage` |
| `GET /sessions/{id}/posterior` | Pesos (priori e posteriori), intervalos e diagnósticos | `PosteriorOut` |
| `GET /sessions/{id}/posterior/trace?feature=log_price` | Traço das 4 primeiras cadeias de um peso, com os 250 pontos guardados de cada uma (corte C4) | `TraceOut` |
| `GET /listings/{id}?session_id=` | Detalhe do imóvel, com score, explicação e vistoria da sessão | `ListingDetailOut` |
| `PUT /sessions/{id}/inspections/{listing_id}` | Substitui os ajustes da vistoria desse imóvel | `ListingDetailOut` |
| `GET /experiment/summary?run_id=` | Métricas agregadas da última rodada (ou da `run_id` pedida) | `ExperimentSummary` |

**No prazo curto:** `GET /listings/{id}` e `PUT /sessions/{id}/inspections/{listing_id}` só são implementadas se João reverter o corte C1 (tarefa E17). Sem C1, o feed devolve `inspection_delta = 0`.

### Schemas principais (Pydantic)

```python
class SessionCreate(BaseModel):
    mode: Literal["product", "demo", "collection"] = "product"
    city: str
    purpose: Literal["sale", "rent"]
    price_min: Decimal = Field(gt=0)
    price_max: Decimal = Field(gt=0)
    persona_slug: Literal["familia", "investidor", "estudante"]
    consent: bool = False
    # model_validator: price_min < price_max; city="Goiânia" e purpose="sale" em todos os modos; collection exige consent=True; o servidor gera participant_code

class SessionOut(BaseModel):
    id: UUID; mode: str; city: str; purpose: str
    price_min: Decimal; price_max: Decimal; persona_slug: str
    target_pairs: int; answered: int; status: Literal["comparing", "done"]

class ListingCard(BaseModel):
    id: UUID; code: str; title: str; neighborhood: str; city: str
    purpose: str; kind: str; price_brl: Decimal; area_m2: float
    bedrooms: int; bathrooms: int; parking: int; dist_center_km: float
    age_years: int; leisure_count: int; pet_friendly: bool; doorman_24h: bool
    illustration: str

class PairOut(BaseModel):
    position: int; total: int
    listing_a: ListingCard; listing_b: ListingCard

class AnswerIn(BaseModel):
    chosen: Literal["A", "B"]
    response_ms: int = Field(ge=0, le=600_000)

class AnswerOut(BaseModel):
    answered: int; total: int; done: bool
    diagnostics: "Diagnostics | None"   # None no modo coleta

class Reason(BaseModel):
    feature_key: str; text: str; contribution: float

class FeedItem(BaseModel):
    listing: ListingCard
    score: int                      # 0..100, já com a vistoria
    affinity_pct: float             # 100 x afinidade, sem a vistoria
    interval: tuple[float, float]   # percentis 5 e 95, em %
    inspection_delta: int
    reasons: list[Reason]           # vazia quando method=persona
    rank: int

class FeedPage(BaseModel):
    items: list[FeedItem]; next_offset: int | None
    method: Literal["bayes", "persona"]; n_comparisons: int

class Diagnostics(BaseModel):
    accept_rate: float; rhat_max: float; ess_min: float
    step_size: float; elapsed_ms: int; ok: bool

class WeightOut(BaseModel):
    feature_key: str; label: str
    prior_mean: float; prior_sd: float
    post_mean: float; post_sd: float; ci_low: float; ci_high: float

class PosteriorOut(BaseModel):
    n_comparisons: int; weights: list[WeightOut]; diagnostics: Diagnostics
```

### Regras da API

- **Idempotência:** `POST /comparisons/{position}` em uma posição já respondida devolve `409 pair_already_answered`. Uma posição diferente da pendente devolve `409 pair_out_of_order`.
- **Retomada:** `GET /next-pair` devolve o par pendente (`chosen IS NULL`), se houver, em vez de criar outro. Recarregar a página não pula pares.
- **Fim:** quando `answered == target_pairs`, `GET /next-pair` devolve `204` sem corpo, e `status` da sessão passa a `done`. `POST` numa sessão `done` devolve `409 session_done`.
- **Candidatos:** pares e feed usam o mesmo conjunto, calculado por uma única função `candidate_listings(session)`: imóveis da cidade e da finalidade da sessão com preço entre 0,85 × `price_min` e 1,15 × `price_max`; se forem menos de 20, todos os imóveis da cidade e da finalidade. A lista é sempre ordenada por `code`.
- **Feed:** com 0 pares respondidos, usa amostras da priori. O parâmetro opcional `at=N` devolve o feed calculado com os N primeiros pares (`at=0` é só a priori), usado na alternância Antes e Depois. `limit` vai de 1 a 50, com padrão 30. `offset` existe e tem padrão 0, mas o front-end usa só a primeira página. Ordem: afinidade média decrescente; empate pelo `code`.
- **Cache:** o ranking é guardado em memória por `(session_id, n_comparisons, method)`, até 128 entradas.
- **Erros:** formato único `{"detail": {"code": "...", "message": "..."}}`, com mensagem em pt-BR. Códigos: `session_not_found` (404), `listing_not_found` (404), `pair_already_answered` (409), `pair_out_of_order` (409), `session_done` (409), `validation_error` (422), `not_available` (501). Um handler global converte o `RequestValidationError` do FastAPI para esse formato.
- **CORS:** liberado só para `http://localhost:5173` (desenvolvimento). Com o Docker Compose, o Nginx serve front-end e API na mesma origem.
- **Configuração (`.env`):** `DATABASE_URL`, `MCMC_CHAINS=16`, `MCMC_WARMUP=1000`, `MCMC_DRAWS=2000`, `MCMC_THIN=8`, `PRIOR_SD=1.0`, `PAIRS_DEMO=3`, `PAIRS_PRODUCT=8`, `PAIRS_COLLECTION=20`, `CATALOG_SEED=42`, `LOG_LEVEL=INFO`, `CORS_ORIGINS=http://localhost:5173`.

## 7. Front-end

São 7 rotas no MVP, mais uma condicional. O fluxo principal é onboarding → comparações → feed. Tudo é pensado primeiro para o celular, porque os colegas da coleta respondem pelo telefone. **Esta seção dá o comportamento; o layout e os textos exatos estão nos mockups aprovados (1.6) e em `copy.ts`.**

| Rota | Tela | Mockup | Conteúdo | Tarefa |
| --- | --- | --- | --- | --- |
| `/coleta` | Coleta | M1 + M4 | Tela inicial, consentimento, faixa de preço (Goiânia, compra), persona, 20 pares e agradecimento; o servidor gera o código do participante | E08 (primeira a ficar pronta) |
| `/` | Início | M2 | Frase "Pare de filtrar. Comece a escolher.", botão Começar e botão Modo demo | E11 |
| `/comecar` | Onboarding | M3 | Passo 1: faixa de preço (Goiânia, compra). Passo 2: cartões das 3 personas | E11 |
| `/demo` | Modo demo | M3b | 3 cartões de persona; um toque cria a sessão `demo` com `demo_defaults` e vai para `/comparar` | E11 |
| `/comparar` | Comparações | M4 | Dois cartões lado a lado (empilhados no celular), barra de progresso, atalhos ← e → | E12 |
| `/feed` | Feed | M5 | Lista de até 30 imóveis com selo de score, intervalo e até 4 motivos \[C2\]; alternância Antes e Depois | E12 |
| `/modelo` | Painel do modelo | M6 | Pesos da priori e da posteriori com intervalos; traço das cadeias \[C4\]; diagnósticos | E13 |
| `/experimento` | Painel do experimento | M7 | Acurácia por número de pares (uma linha por método) e por participante | E14 |
| `/imovel/:id` | Detalhe e vistoria | M8 | Só se o corte C1 for revertido | E17 |

### Comportamento de cada tela

**Onboarding (`features/onboarding`).** Um formulário do React Hook Form em dois passos, com um schema Zod por passo. A faixa de preço é um `Slider` de duas alças com campos numéricos sincronizados. Os limites vêm do único segmento de `GET /meta/options`, e o slider anda em passos de R$ 10 mil. Ao enviar, chama `POST /sessions`, guarda o `sessionId` no Zustand e navega para `/comparar`.

```ts
export const step1Schema = (seg: Segment) =>
  z.object({
    priceMin: z.number().positive(),
    priceMax: z.number().positive(),
  }).superRefine((v, ctx) => {
    if (v.priceMin >= v.priceMax) ctx.addIssue({ code: "custom", path: ["priceMax"], message: "O máximo precisa ser maior que o mínimo" });
    if (v.priceMax < seg.price_floor) ctx.addIssue({ code: "custom", path: ["priceMax"], message: "Nenhum imóvel nessa faixa" });
  });
export const step2Schema = z.object({ personaSlug: z.enum(["familia", "investidor", "estudante"]) });
export const collectionSchema = z.object({
  consent: z.literal(true, { error: "É preciso concordar para participar" }),
});
```

**Comparações (`features/compare`).** Busca `GET /next-pair`. O cartão escolhido sai com animação do Framer Motion (`AnimatePresence`), e o tempo de resposta é medido com `performance.now()` desde que o par aparece. As teclas ← e → escolhem; botões são desabilitados enquanto a resposta é enviada, para evitar duplo clique. Ao receber `done: true`, navega para `/feed` (ou para a tela de agradecimento, no modo coleta). O próximo par é pré-carregado com `queryClient.prefetchQuery` assim que a resposta é aceita.

**Feed (`features/feed`).** Uma única consulta `useQuery` a `GET /sessions/{id}/feed?limit=30`, sem rolagem infinita. Cada cartão mostra o selo com o score (ex.: "87"), com o texto "87% de chance de você preferir este a um imóvel típico" no tooltip, o intervalo ("entre 71 e 95") e os motivos como chips \[C2\]. A alternância **Antes e Depois** faz duas consultas: `at=0` (só a priori) e `at=<n respondidos>`. Os itens usam `motion.li` com `layout` e `key = listing.id`, então a troca anima a reordenação sozinha. Esse é o "momento uau" da demo. Sem link para o detalhe enquanto o corte C1 valer.

**Detalhe e vistoria (`features/listing`) · só com C1 revertido.** Lista os itens de `GET /meta/inspection-items` (ex.: "Rua barulhenta, −10"; "Boa iluminação, +5"), cada um com um interruptor e um slider de −10 a +10. O envio usa `PUT /inspections/{listing_id}` com atualização otimista do score (`onMutate`, com rollback em `onError`).

**Painel do modelo (`features/model-panel`).** Gráfico de intervalos (Recharts, `ComposedChart` com barras de erro): para cada característica, um ponto para a média da priori e outro para a da posteriori, com a faixa de 5% a 95%. Abaixo, o traço de 4 das 16 cadeias de um peso escolhido em um `Select`, e um quadro com aceitação, R-hat, ESS e tempo. É a tela que conversa com a banca.

**Painel do experimento (`features/experiment`).** Linhas de acurácia contra n\_train (3, 5, 10), uma por método, com faixa de ±1 desvio, e uma tabela com acurácia e perda logarítmica. Se a rodada tiver participantes simulados, um aviso fixo diz "Dados simulados".

### Dados e estado

- **Cliente:** `openapi-fetch` com o tipo `paths` de `src/api/schema.d.ts` e `baseUrl: "/api/v1"`. No dev, o Vite faz proxy de `/api` para `http://localhost:8000`.
- **Chaves de query:** `['meta', 'options']`, `['meta', 'personas']`, `['session', id]`, `['pair', id]`, `['feed', id, method, at]`, `['posterior', id, n]`, `['trace', id, n, feature]`, `['listing', id, sessionId]`, `['experiment', runId]`. Todas ficam em `src/api/queries.ts` como funções `queryOptions(...)`.
- **Padrões do `QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`. Dados de `meta` usam `staleTime: Infinity`, porque não mudam durante a sessão.
- **Depois de responder um par:** invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
- **Zustand:** `{ sessionId, mode, setSession, reset }`, com `persist` no `localStorage` dentro de `try/catch`. Sem `sessionId` válido, as rotas protegidas redirecionam para `/comecar`.

### Visual e acessibilidade

- Componentes do shadcn/ui, sobre Base UI: `Button`, `Card`, `Badge`, `Progress`, `Slider`, `Select`, `RadioGroup`, `Tabs`, `Tooltip`, `Switch`, `Skeleton`, `Sonner` (avisos).
- Fonte Geist instalada via `@fontsource-variable/geist`, para funcionar offline. Nada de Google Fonts.
- Cores como variáveis CSS do tema do shadcn, com modo escuro. O selo de score tem três faixas (0 a 39, 40 a 69, 70 a 100) e sempre mostra o número, para não depender só da cor.
- Valores com `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 })`.
- Contraste AA, foco visível, `aria-live="polite"` na barra de progresso e textos alternativos nas ilustrações.
- Estados de carregamento com `Skeleton`, e erros com aviso e botão "Tentar de novo". Um `ErrorBoundary` na raiz mostra uma tela de erro amigável.

## 8. Cronograma e tarefas (04/11 a 09/11)

São 9 tarefas do arquiteto (A), 17 do executor (E) e 7 checkpoints e 2 gates de aprovação de João (J), em 6 dias de implementação. A coleta precisa estar no ar na quinta à tarde, para os colegas terem tempo de responder enquanto o resto é construído. Por isso, o primeiro dia inteiro está voltado para ela.

&#91;embedded content: cronograma · 04/11 a 11/11, por papel\]

Claude constrói o motor e desenha as telas; o executor implementa o resto em paralelo; João aprova e responde aos checkpoints todo dia. Depois do congelamento, só ensaio.

### 8.1 Visão por dia

| Dia | Claude (A) | Executor (E) | João (J) | Marco ao fim do dia |
| --- | --- | --- | --- | --- |
| qua 04/11 | A01 tema, textos e mockups M1 e M4 (até 14h); A02 características, catálogo e personas; A03 modelo e pares aleatórios | E01 a E05; E06 seed (depois de A02) | Aprovar M1 e M4 (gate G1) até 16h; CP1; CP2 | Banco com 300 imóveis; G1 aprovado |
| qui 05/11 | A04 mockups M2, M3, M3b, M5, M6 e M7 (até 13h); A05 Metropolis-Hastings e diagnósticos | E07 API da coleta; E08 tela da coleta; E09 Docker completo, exportação e túnel (até 17h) | Aprovar G2 até 18h; enviar o link da coleta às 18h; CP3 | Coleta no ar |
| sex 06/11 | A06 afinidade, BALD, baselines e interface completa (até 13h); A07 avaliação e simulação; A-REV1 | E10 API do feed, do modelo e do experimento (depois de A06); E11 início, onboarding e demo | CP4 | Feed calculado pela API |
| sáb 07/11 | A-REV2 e ajuste das personas olhando o feed | E12 comparações e feed; E13 painel do modelo; E14 painel do experimento | CP5; lembrete aos colegas | Fluxo da demo completo |
| dom 08/11 | A08 experimento com dados reais (a partir das 12h) | E15 `make check`, README e `make demo`; correções da A-REV2 | Encerrar a coleta às 12h; CP6 | Painel do experimento com dados reais |
| seg 09/11 | A09 revisão final e roteiro da demo | E16 correções e teste offline; E17 só se autorizado | Decidir os cortes às 12h; CP7; aprovar o congelamento às 22h | Tag `v1.0.0` |
| ter 10/11 | Só correções que impeçam a demo, com autorização de J | Nada, salvo correção pedida | Ensaio, checklist da seção 10, vídeo de 60 s | Pronto para a banca |
| qua 11/11 | — | — | Apresentação | — |

**Dependências que travam o trabalho.** E05 espera A01 (precisa de `theme.css`). E06 espera A02. E07 espera A03 (`seed_for` e `random_pairs`). E08 espera M1 e M4 aprovados. E10 espera A06 marcada como concluída em `docs/STATUS.md`. E11 a E14 esperam G2. Se uma dependência atrasar, o executor passa para a próxima tarefa sem dependência pendente e registra o atraso em `docs/STATUS.md`.

**Se o dia atrasar.** A ordem de sacrifício é: primeiro os cortes condicionais da seção 1.7 (C2, C3, C4, nesta ordem); depois, o ajuste fino visual. Nunca o motor, a coleta, os testes do motor ou o teste offline.

### 8.2 Tarefas do arquiteto (Claude)

- [ ] **A01 · Tema, textos e mockups do gate G1** · qua 04/11, até 14h · depende de: nada
  - **Objetivo:** definir a identidade visual e as telas de coleta e de comparação antes de o executor implementá-las.
  - **Arquivos:** `frontend/src/styles/theme.css`; `frontend/src/lib/copy.ts`; `docs/mockups/m1-coleta.html` e `.md`; `docs/mockups/m4-comparar.html` e `.md`; `docs/mockups/APPROVAL.md`.
  - **Passos:**
    1. Primeiro, `theme.css`, para destravar E05: variáveis CSS no formato do shadcn (`--background`, `--foreground`, `--card`, `--card-foreground`, `--primary`, `--primary-foreground`, `--secondary`, `--muted`, `--muted-foreground`, `--accent`, `--border`, `--input`, `--ring`, `--destructive`, `--radius`) para o tema claro (`:root`) e o escuro (`.dark`), mais `--score-low`, `--score-mid`, `--score-high` e `--font-sans: "Geist Variable", sans-serif`. Contraste AA em todos os pares texto e fundo.
    2. `copy.ts`: `export const copy = { common: {...}, collection: {...}, compare: {...} } as const;` com todos os textos das telas M1 e M4, inclusive mensagens de erro e de validação. Textos com variáveis viram funções, por exemplo `progress: (i: number, n: number) => \`Par ${i} de ${n}\`\`.
    3. Mockups no formato da seção 1.6. O cartão de imóvel mostra ilustração, título, bairro, preço, área, quartos, banheiros, vagas, idade, lazer, distância ao centro e os selos "aceita pet" e "portaria 24 h". M1 inclui a tela inicial (o que é o experimento, o que a pessoa fará, como as respostas serão usadas e que nenhum dado pessoal é coletado), o formulário (consentimento, faixa de preço, persona; Goiânia e compra são fixas, e o código vem do servidor), o uso de M4 para os 25 pares e a tela de agradecimento.
    4. Apresentar a João (1.6) e registrar a decisão em `APPROVAL.md`.
  - **Pronto quando:** M1 e M4 aparecem como "aprovado" em `APPROVAL.md`.
- [ ] **A02 · Características, catálogo simulado e personas** · qua 04/11 · depende de: E03
  - **Arquivos:** `backend/app/engine/features.py`; `backend/app/seed/__init__.py`; `backend/app/seed/catalog.py`; `backend/app/seed/personas.yaml`; `backend/app/seed/inspection_items.yaml`; `backend/tests/engine/test_features.py`; `backend/tests/engine/test_catalog.py`.
  - **Especificação:** seções 5.1, 5.3 e 5.10, mais as regras do catálogo a seguir.
  - **Catálogo:** `generate_catalog(seed: int) -> list[ListingRow]`, em que `ListingRow` é uma dataclass imutável com os campos da tabela `listings` (seção 4), exceto `id` e `created_at`. São 300 imóveis, todos em Goiânia e à venda (decisão de João em 04/11). Tudo vem de `rng = np.random.default_rng(seed)`, gerados em ordem de índice.
    - `code`: `GYN-V-{0001..0300}`.
    - Bairros, com distância ao centro: Setor Central 1 km, Setor Oeste 2, Setor Universitário 2, Setor Marista 3, Setor Bueno 4, Jardim Goiás 5, Setor Pedro Ludovico 5, Jardim América 6, Parque Amazônia 8. `dist_center_km` = distância do bairro + U(−0,5; 0,5), no mínimo 0,3.
    - `kind`: casa com probabilidade 0,35.
    - `bedrooms`: apartamento sorteado em \[1, 2, 3, 4\] com probabilidades \[0,15; 0,40; 0,35; 0,10\]; casa em \[2, 3, 4, 5\] com \[0,15; 0,40; 0,30; 0,15\].
    - `area_m2` = exp(N(ln(28 + 22 × quartos) + 0,15 se casa; 0,18)), com uma casa decimal.
    - `bathrooms`: inteiro sorteado entre um mínimo e um máximo. O máximo é o menor valor entre os quartos e a área / 25 arredondada para baixo, sendo no mínimo 1. O mínimo é a metade dos quartos arredondada para cima, sem passar do máximo. `parking` = arredondar(área / 45 + N(0; 0,6)), limitado a \[0, 4\]. `age_years`: inteiro de 0 a 40.
    - `leisure_count`: apartamento em \[0, 1, 2, 3\] com \[0,2; 0,3; 0,3; 0,2\]; casa com \[0,6; 0,3; 0,1; 0\].
    - `doorman_24h`: 0,70 em apartamentos e 0,10 em casas. `pet_friendly`: 0,60.
    - Preço de venda: exp(8,5 + 1,0 × ln(área) + 0,08 × vagas − 0,03 × distância − 0,006 × idade + 0,05 × lazer + 0,04 × portaria + N(0; 0,12)), arredondado para R$ 1.000.
    - Claude só pode ajustar o intercepto (8,5), para que pelo menos 95% dos preços fiquem entre R$ 150 mil e R$ 2,5 milhões. Os valores finais vão para `docs/decisions.md`.
    - `title`: "Apartamento de 3 quartos no Setor Bueno" ou "Casa de 1 quarto no ..." (singular com 1). `illustration`: `apartment-1` a `apartment-3` ou `house-1` a `house-3`.
  - **`personas.yaml`:** lista com `slug`, `name`, `description` (1 frase), `prior_mean` (as 12 chaves da tabela 5.3), `prior_sd` (12 chaves, todas 1,0) e `demo_defaults` (`city`, `purpose`, `price_min`, `price_max`, com os valores da seção 5.3).
  - **`inspection_items.yaml`:** lista com `key`, `label` e `delta`: `noisy_street` Rua barulhenta −10; `humidity` Umidade ou mofo −8; `needs_renovation` Precisa de reforma −7; `low_light` Pouca luz natural −5; `good_light` Boa iluminação +5; `quiet_neighborhood` Vizinhança tranquila +6; `walkable_shops` Comércio a pé +5; `nice_view` Vista bonita +4.
  - **Testes:** a mesma semente gera o mesmo catálogo; 300 imóveis, todos em Goiânia e à venda; códigos únicos; faixas de preço (95%); `bathrooms ≤ bedrooms`, no máximo 1 banheiro a cada 25 m² e pelo menos metade dos quartos, salvo quando a área não permite; a mediana vira 0 depois de `standardize`; IQR zero cai para o desvio padrão e depois para 1; `bedrooms_sq` vale 0 para 3 quartos antes da padronização; `raw_matrix` devolve (n, 12).
  - **Verificação:** `cd backend && uv run pytest tests/engine -q && uv run mypy app/engine`.
  - **Checkpoint:** CP1.
- [ ] **A03 · Modelo e pares aleatórios** · qua 04/11 · depende de: A02
  - **Arquivos:** `backend/app/engine/model.py`; `backend/app/engine/pairs.py` (só `seed_for` e `random_pairs` nesta tarefa); `backend/app/engine/__init__.py` (só com os nomes já implementados); `backend/tests/engine/test_model.py`; `backend/tests/engine/test_pairs.py`.
  - **Especificação:** seções 5.2, 5.7 (modo coleta) e 5.10.
  - **Testes:** `sigmoid` sem `nan` nem aviso com u = ±1000; `log_likelihood` igual a `-sklearn.metrics.log_loss(np.ones(m), p, labels=[0, 1]) * m` em dados aleatórios; com m = 0, `log_posterior` igual a `log_prior`; `random_pairs(50, 40, rng)` sem par repetido e com cada índice no máximo 3 vezes; mesma semente, mesma lista; em 2.000 pares, o lado esquerdo fica com o índice menor entre 45% e 55% das vezes.
  - **Pronto quando:** verificação da A02 passa, CP2 concluído e A03 registrada em `docs/STATUS.md` (isso libera E07).
- [ ] **A04 · Mockups do gate G2** · qui 05/11, até 13h · depende de: A01
  - **Arquivos:** `docs/mockups/m2-inicio`, `m3-onboarding`, `m3b-demo`, `m5-feed`, `m6-modelo`, `m7-experimento` (`.html` e `.md` de cada); `frontend/src/lib/copy.ts` (acrescentar as chaves dessas telas); `docs/mockups/APPROVAL.md`.
  - **Requisitos de UX:** o fluxo M3b → M4 → M5 cabe em 60 segundos para um visitante; o "momento uau" de M5 é a reordenação animada ao trocar Antes e Depois; M6 explica cada número de diagnóstico em uma frase para leigos ("R-hat perto de 1: as cadeias concordam"); M7 mostra o aviso "Dados simulados" quando `simulated = true` e um estado vazio quando não houver resultados. M5 mostra o selo com as três faixas de cor do tema e sempre o número.
  - **Pronto quando:** as seis telas aparecem como "aprovado" em `APPROVAL.md`.
- [ ] **A05 · Metropolis-Hastings e diagnósticos** · qui 05/11 · depende de: A03
  - **Arquivos:** `backend/app/engine/mcmc.py`; `backend/app/engine/diagnostics.py`; `__init__.py`; `backend/tests/engine/test_mcmc.py`; `backend/tests/engine/test_diagnostics.py`.
  - **Especificação:** seções 5.4, 5.5 e 5.10 (`fit_posterior`).
  - **Testes:** (a) alvo gaussiano conhecido de 12 dimensões: média a menos de 0,1 e variância a menos de 10% das verdadeiras; (b) sem pares, as amostras reproduzem a priori; (c) usuário sintético com w verdadeiro e 300 pares: correlação entre a média da posteriori e w maior que 0,9; (d) priori fraca (σ = 10) e 300 pares: média da posteriori a menos de 0,15 do MAP calculado com `scipy.optimize.minimize`; (e) mesma semente, mesmas amostras; (f) R-hat abaixo de 1,05 e ESS acima de 400 nesses casos; (g) 40 pares em menos de 250 ms (`@pytest.mark.perf`).
  - **Checkpoint:** CP3.
- [ ] **A06 · Afinidade, explicação, BALD, baselines e interface completa** · sex 06/11, até 13h · depende de: A05
  - **Arquivos:** `backend/app/engine/affinity.py`; `backend/app/engine/pairs.py` (`next_pair_bald`); `backend/app/engine/baselines.py`; `__init__.py` (todos os nomes da 5.10, exceto os de `evaluation`); testes correspondentes.
  - **Especificação:** seções 5.6 a 5.8 e 5.10.
  - **Testes:** afinidade sempre em \[0, 1\]; `to_score` sempre em \[0, 100\], inclusive com delta de −80 e +80; o imóvel típico (z = 0) tem afinidade 0,5; `explain` devolve no máximo 4 motivos e ignora |c| < 0,1; BALD ≥ 0 em todos os candidatos e nunca repete um par de `shown`; com amostras quase iguais, BALD perto de 0 em todos os pares; `fit_mle` treina com 1 par; os quatro métodos de `predict_proba` devolvem valores em (0, 1).
  - **Pronto quando:** testes passam, CP4 concluído e "A06 concluída: interface 5.10 completa" registrada em `docs/STATUS.md` (libera E10).
- [ ] **A07 · Avaliação, simulação e relatório** · sex 06/11 · depende de: A06, E09
  - **Arquivos:** `backend/app/engine/evaluation.py`; `backend/app/analysis/__init__.py`; `backend/app/analysis/report.py`; as funções `simulate` e `evaluate` em `backend/app/cli.py`; `backend/tests/engine/test_evaluation.py`.
  - **Especificação:** seção 5.9 e o formato JSON da tarefa E09.
  - **`simulate --participants 10 --out data/collected/pairs_simulated.json`:** participantes S01 a S10, personas em rodízio (familia, investidor, estudante), segmento de `demo_defaults` da persona, w verdadeiro = μ + N(0; 0,7²), 25 pares de `random_pairs` sobre os candidatos e escolhas por `simulate_choices`. `session_id` fica `null`.
  - **`evaluate --from-json <arquivo> --out data/results`:** monta D de cada participante (z = `standardize(t, center, scale)`; vencedor = esquerda se `chosen = "A"`), roda `evaluate_participant` e grava `results.csv` (colunas: `run_id, participant_code, method, n_train, split_seed, n_test, accuracy, log_loss`, com um `run_id` UUID por execução), `summary.csv` (colunas: `method, n_train, acc_mean, acc_sd, ll_mean, ll_sd, n_participants`) e as figuras `accuracy_vs_ntrain.png` e `accuracy_by_participant.png` (seção 5.9). Imprime a tabela resumo no terminal.
  - **Pronto quando:** nos dados simulados, `bayes` e `mle` superam `equal` com n\_train = 15, e Claude mostra as figuras a João.
- [ ] **A-REV1 · Revisão do back-end** · sex 06/11, fim do dia · depende de: E07 a E10
  - Ler o diff de E07 a E10 contra as seções 4, 6 e 8.3; rodar `make check`; confirmar que `services/` só importa `app.engine`; medir o tempo de resposta de `POST /comparisons` no modo demo (meta: menos de 300 ms).
  - Cada problema vira uma tarefa `FIX-n` em `docs/STATUS.md`, com arquivo, o que está errado e o que a especificação diz. O executor as resolve antes da próxima tarefa.
- [ ] **A-REV2 · Revisão das telas e das personas** · sáb 07/11, noite · depende de: E11 a E14
  - Abrir cada tela ao lado do seu mockup, em 375 px e 1280 px, e conferir os critérios de aceite visual. Cronometrar o fluxo da demo (meta: 60 s).
  - Olhar os 10 primeiros imóveis do feed de cada persona com 0 pares. Se algum resultado for absurdo (ex.: Família com quitinetes no topo), ajustar `personas.yaml` e explicar a João no CP5.
  - Problemas viram `FIX-n`, como na A-REV1.
- [ ] **A08 · Experimento com dados reais** · dom 08/11, a partir das 12h · depende de: coleta encerrada, A07
  - Rodar `make evaluate`. Se houver menos de 5 participantes com pelo menos 20 pares, rodar também `simulate` e `evaluate` e deixar o painel com os dados reais, mais um aviso de quantos são.
  - Escrever `docs/results.md` (até 1 página): número de participantes, tabela de acurácia e perda logarítmica por método em n\_train = 3, 5 e 10, se H1 e H2 se confirmaram e as limitações (seção 11 do guia).
  - **Checkpoint:** CP6.
- [ ] **A09 · Revisão final e roteiro da demo** · seg 09/11 · depende de: E15
  - Rodar com João o roteiro manual offline da seção 9. Problemas bloqueantes viram `FIX-n` para a E16.
  - Escrever `docs/demo-script.md`: a fala de 60 segundos para visitantes, a fala de 3 minutos para professores e respostas de até 2 frases para as 18 perguntas da seção 12 do guia.
  - **Checkpoint:** CP7. Depois da aprovação de João às 22h, criar a tag `v1.0.0`.

### 8.3 Tarefas do executor (OpenCode Go)

Cada tarefa é iniciada com o pedido padrão da seção 1.5. O campo **Arquivos** é a lista completa do que pode ser criado ou editado. A **Verificação** é obrigatória e tem de passar sem nenhum teste removido ou marcado para pular.

- [ ] **E01 · Repositório e instruções dos agentes** · qua 04/11 · depende de: nada
  - **Arquivos:** a estrutura de pastas da seção 3 (pastas vazias com `.gitkeep`); `.gitignore` (Python, Node, `.env`, `.venv/`, `node_modules/`, `dist/`, `__pycache__/`, `.pytest_cache/`); `.editorconfig` (UTF-8, LF, 4 espaços em Python, 2 nos demais); `.env.example` (todas as variáveis da seção 6, com os valores padrão); `Makefile`; `README.md` (só o título e "em construção"); `docs/PLAN.md` (João fornece o conteúdo: exportação deste documento em Markdown); `docs/STATUS.md`; `docs/decisions.md`; `docs/CHECKPOINTS.md`; `docs/mockups/APPROVAL.md`; `AGENTS.md`; `CLAUDE.md`.
  - **`AGENTS.md`** (exatamente este conteúdo):

  ```markdown
  # ImobScore — instruções para o executor (papel E)
  Antes de qualquer tarefa, leia o arquivo da tarefa pedida (docs/tasks/<ID>-*.md) e docs/STATUS.md.
  - O arquivo da tarefa é autocontido e é o que vale. Consulte docs/PLAN.md só se faltar algo nele, lendo apenas a seção necessária, nunca o arquivo inteiro.
  - Faça somente a tarefa E indicada no pedido. Uma por vez.
  - Edite apenas os arquivos listados em "Arquivos permitidos" no arquivo da tarefa.
  - Nunca edite: backend/app/engine/, backend/app/seed/, backend/app/analysis/, backend/tests/engine/, docs/mockups/, frontend/src/styles/theme.css, frontend/src/lib/copy.ts, docs/PLAN.md, docs/GUIDE.md, docs/tasks/.
  - Importe o motor apenas com "from app.engine import ..." (nomes da seção 5.10 do plano, reproduzida nas tarefas que a usam).
  - Textos de tela vêm de frontend/src/lib/copy.ts. Layout e cores vêm do mockup aprovado e de theme.css. Não escreva textos visíveis direto nos componentes.
  - Se algo não estiver especificado, não decida: escreva a pergunta em docs/STATUS.md, em "Perguntas abertas", e pare.
  - Não adicione dependências nem mude versões. Não apague, pule nem afrouxe testes.
  - Termine só com todos os comandos de "Verificação" passando. Registre em docs/STATUS.md e faça um commit "tipo(escopo): ID título".
  - Commits e PRs não citam agentes nem ferramentas de IA: sem "Co-Authored-By", sem "Generated with" e sem menção equivalente.
  - Se uma verificação falhar duas vezes seguidas, pare e marque a tarefa como "precisa de revisão do arquiteto".
  ```
  - **`CLAUDE.md`** (exatamente este conteúdo):

  ```markdown
  # ImobScore — instruções para o Claude (papel A, arquiteto)
  Antes de qualquer tarefa, leia docs/PLAN.md e docs/STATUS.md.
  - Faça só as tarefas A e A-REV da seção 8.2, na ordem.
  - Siga o protocolo de checkpoints da seção 1.4: ao terminar cada módulo do motor, explique a João, faça as 3 perguntas, espere cada resposta, tire todas as dúvidas e registre em docs/CHECKPOINTS.md. Só João declara "Entendido: sim". Sem isso, não faça commit do módulo seguinte.
  - Siga a seção 1.6 para mockups. Nenhuma tela vai para o executor sem "aprovado" em docs/mockups/APPROVAL.md.
  - Mantenha a interface da seção 5.10. Se precisar mudá-la, avise João e atualize docs/PLAN.md na mesma alteração.
  - Ao mudar uma especificação em docs/PLAN.md, leve a mudança, na mesma alteração, às tarefas E de docs/tasks/ que reproduzem o trecho.
  - Decisões não previstas: escolha a opção mais simples compatível com o plano e registre em docs/decisions.md.
  - Commits e PRs não citam agentes nem ferramentas de IA: sem "Co-Authored-By", sem "Generated with" e sem menção equivalente.
  - Atualize docs/STATUS.md ao fim de cada tarefa.
  ```
  - **`docs/STATUS.md`** começa com os títulos `## Em andamento`, `## Concluídas (ID · data · resumo da verificação)`, `## Correções pendentes (FIX-n)`, `## Perguntas abertas (ID · pergunta · quem responde)` e `## Bloqueios`. `docs/CHECKPOINTS.md` começa com uma seção vazia por checkpoint, de CP1 a CP7. `APPROVAL.md` começa com o cabeçalho `| Tela | Versão | Status | Data | Observações de João |` e uma linha por tela de M1 a M8, com status "pendente".
  - **`Makefile`**, com estes alvos e comandos:

  ```make
  API = docker compose exec api python -m app.cli
  .PHONY: help up down dev seed demo check test export simulate evaluate tunnel reset
  help:     ## lista os alvos
  	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/ -/'
  up:       ## sobe db, api e web
  	docker compose up -d --build
  down:     ## para tudo
  	docker compose down
  dev:      ## sobe só o banco e mostra como rodar API e front localmente
  	docker compose up -d db
  	@echo "Terminal 1: cd backend && uv run uvicorn app.main:app --reload --port 8000"
  	@echo "Terminal 2: cd frontend && pnpm dev"
  seed:     ## recria catálogo, personas e estatísticas
  	$(API) seed --force
  demo:     ## sobe tudo, semeia se vazio e abre o modo demo
  	docker compose up -d --build
  	$(API) seed --if-empty --with-results
  	@xdg-open http://localhost:8080/demo 2>/dev/null || open http://localhost:8080/demo
  check:    ## lint, tipos e testes do back-end e do front-end
  	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app/engine && uv run pytest -q -m "not perf"
  	cd frontend && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run
  test:     ## só os testes
  	cd backend && uv run pytest -q
  	cd frontend && pnpm test:run
  export:   ## grava os pares da coleta em data/collected/pairs.json
  	$(API) export --out data/collected/pairs.json
  simulate: ## gera participantes simulados
  	$(API) simulate --participants 10 --out data/collected/pairs_simulated.json
  evaluate: ## exporta, avalia e carrega os resultados no banco
  	$(API) export --out data/collected/pairs.json
  	$(API) evaluate --from-json data/collected/pairs.json --out data/results
  	$(API) load-results data/results/results.csv
  tunnel:   ## expõe a porta 8080 para a coleta
  	cloudflared tunnel --url http://localhost:8080
  reset:    ## apaga o banco (pede confirmação)
  	@read -p "Apagar o banco? [s/N] " r && [ "$$r" = "s" ] && docker compose down -v
  ```
  - **Verificação:** `make help` lista os 13 alvos; `git status` limpo depois do commit.
- [ ] **E02 · Banco no Docker** · qua 04/11 · depende de: E01
  - **Arquivos:** `docker-compose.yml` (só o serviço `db` da seção 10 nesta tarefa); `docker/initdb/01-test-db.sql` (`CREATE DATABASE imobscore_test OWNER imobscore;`).
  - **Verificação:** `docker compose up -d db` fica `healthy`; `docker compose exec db psql -U imobscore -d imobscore_test -c "select 1"` responde.
- [ ] **E03 · Esqueleto do back-end** · qua 04/11 · depende de: E02
  - **Arquivos:** `backend/pyproject.toml`; `backend/uv.lock`; `backend/app/__init__.py`; `backend/app/main.py`; `backend/app/config.py`; `backend/app/db.py`; `backend/app/deps.py`; `backend/app/errors.py`; `backend/app/api/__init__.py`; `backend/app/api/v1/__init__.py`; `backend/app/api/v1/health.py`; `backend/tests/conftest.py`; `backend/tests/api/test_health.py`.
  - **Dependências** (`uv add`): `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `psycopg[binary]`, `alembic`, `numpy`, `scikit-learn`, `matplotlib`, `typer`, `pyyaml`. Desenvolvimento (`uv add --dev`): `pytest`, `pytest-cov`, `httpx`, `ruff`, `mypy`, `scipy`. Python 3.12. Nada além disso.
  - **`config.py`:** classe `Settings(BaseSettings)` com os campos e padrões da lista "Configuração" da seção 6, mais `TEST_DATABASE_URL`. `get_settings()` com `lru_cache`.
  - **`main.py`:** cria `FastAPI(title="ImobScore")`, registra o handler de erros de `errors.py` (formato da seção 6), o CORS com `CORS_ORIGINS` e o router `/api/v1`.
  - **`errors.py`:** `class ApiError(Exception)` com `status`, `code` e `message`, e os handlers de `ApiError` e `RequestValidationError` (este devolve `422 validation_error`).
  - **`conftest.py`:** fixture `db` que conecta em `TEST_DATABASE_URL`, abre uma transação por teste e faz rollback no fim; fixture `client` com `TestClient` e `get_db` sobrescrito.
  - **`pyproject.toml`:** Ruff com `line-length = 100` e regras `E, F, I, B, UP`; mypy `strict = true` só para `app.engine.*`; pytest com o marcador `perf` registrado.
  - **Verificação:** `cd backend && uv run pytest -q && uv run ruff check . && uv run ruff format --check .`; `GET /api/v1/health` devolve `{"status": "ok", "db": "ok"}`.
- [ ] **E04 · Modelos do banco e migração** · qua 04/11 · depende de: E03
  - **Arquivos:** `backend/app/models/__init__.py`, `base.py`, `listing.py`, `feature_stats.py`, `persona.py`, `session.py`, `comparison.py`, `posterior.py`, `inspection.py`, `experiment_result.py`; `backend/alembic.ini`; `backend/migrations/` (`env.py` e uma única revisão `0001_initial.py`); `backend/tests/test_migrations.py`.
  - **Especificação:** o DDL da seção 4, exatamente, com SQLAlchemy 2.0 (`Mapped[...]`). Convenção de nomes no `MetaData`: `ix_%(column_0_label)s`, `uq_%(table_name)s_%(column_0_name)s`, `ck_%(table_name)s_%(constraint_name)s`, `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`, `pk_%(table_name)s`. Depois do `--autogenerate`, conferir à mão os `CHECK` e o `gen_random_uuid()`.
  - **Verificação:** um teste roda `upgrade head`, `downgrade base` e `upgrade head` no banco de teste sem erro; `\dt` mostra as 8 tabelas.
- [ ] **E05 · Esqueleto do front-end** · qua 04/11 · depende de: E01, A01 (`theme.css`)
  - **Arquivos:** tudo em `frontend/`, exceto `src/styles/theme.css`, `src/lib/copy.ts` e `src/features/`: `package.json`, `pnpm-lock.yaml`, `vite.config.ts`, `vitest.config.ts`, `tsconfig*.json`, `eslint.config.js`, `.prettierrc`, `components.json`, `index.html`, `src/main.tsx`, `src/app/router.tsx`, `src/app/providers.tsx`, `src/app/layout.tsx`, `src/styles/index.css`, `src/lib/cn.ts`, `src/stores/session-store.ts`, `src/components/ui/*` (gerados pelo shadcn), `src/test/setup.ts`, `src/mocks/handlers.ts` (vazio), `src/app/router.test.tsx`, `public/illustrations/` (6 SVGs simples: `apartment-1..3.svg`, `house-1..3.svg`, desenhos geométricos de um prédio e de uma casa em 3 cores do tema).
  - **Passos:** `pnpm create vite frontend --template react-ts`; copiar dependências e scripts do `package.json` de referência (seção 2), aplicando as regras e os cortes dela; `pnpm dlx shadcn@latest init` escolhendo Base UI; `shadcn add button card badge progress slider select radio-group tabs tooltip switch skeleton sonner checkbox input label form`; `index.css` só com `@import "tailwindcss"; @import "tw-animate-css"; @import "./theme.css";`, apagando as variáveis e o `@theme` que o `shadcn init` gravar nesse arquivo, porque substituiriam o tema, e `@fontsource-variable/geist` importado em `main.tsx`; alias `@/` para `src/`; proxy `/api` para `http://localhost:8000` no `vite.config.ts`.
  - **Router:** rotas `/`, `/coleta`, `/comecar`, `/demo`, `/comparar`, `/feed`, `/modelo`, `/experimento` apontando para um componente temporário `Placeholder` que mostra o nome da rota; rota `*` para a início.
  - **`QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`.
  - **`session-store.ts`:** Zustand com `persist` (chave `imobscore-session`, `localStorage` envolvido em `try/catch`): `{ sessionId: string | null, mode: "product" | "demo" | "collection" | null, setSession(id, mode), reset() }`.
  - **Verificação:** `pnpm build && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run` (o teste do router confere que `/feed` renderiza o placeholder).
- [ ] **E06 · Comando seed** · qua 04/11, noite · depende de: A02, E04
  - **Arquivos:** `backend/app/cli.py` (app Typer, rodado com `python -m app.cli`; deixar as funções `simulate` e `evaluate` para a A07); `o arquivo termina com if __name__ == "__main__": app()`; `backend/app/services/__init__.py`; `backend/app/services/seed_service.py`; `backend/tests/services/test_seed.py`; `backend/tests/conftest.py` (acrescentar uma fixture de sessão, com `autouse=True`, que roda `alembic upgrade head` em `TEST_DATABASE_URL`).
  - **`seed [--force] [--if-empty] [--with-results]`:**
    1. Com `--if-empty` e `listings` não vazia, não fazer nada além do passo 6.
    2. Se existir alguma linha em `sessions` e não houver `--force`, parar com a mensagem "Existem sessões; use --force para apagar tudo".
    3. Em uma transação: `TRUNCATE` de todas as tabelas, com `CASCADE`.
    4. Inserir `generate_catalog(settings.CATALOG_SEED)` em `listings` e as personas de `app/seed/personas.yaml` em `personas`.
    5. Para cada (cidade, finalidade): `T = raw_matrix(listings do segmento)`, `center, scale = fit_stats(T)` e uma linha em `feature_stats` por chave de `FEATURE_KEYS`.
    6. Com `--with-results` e `data/results/results.csv` existente: carregar esse CSV como em `load-results` (E10).
  - **Verificação:** `pytest tests/services/test_seed.py` confere 300 imóveis, 3 personas e 12 linhas de `feature_stats`; rodar duas vezes gera os mesmos códigos e preços.
- [ ] **E07 · API da coleta** · qui 05/11, manhã · depende de: A03, E06
  - **Arquivos:** `backend/app/schemas/__init__.py`, `meta.py`, `session.py`, `listing.py`, `pair.py`; `backend/app/services/listing_service.py` (`candidate_listings`), `session_service.py`, `pair_service.py`; `backend/app/api/v1/__init__.py` (registrar as rotas novas), `meta.py`, `sessions.py`; `backend/app/deps.py` (acrescentar `get_session_or_404`, que levanta `ApiError` 404 `session_not_found`); `backend/tests/api/test_meta.py`, `test_sessions.py`, `test_pairs_collection.py`.
  - **Rotas:** `GET /meta/options`, `GET /meta/personas`, `POST /sessions`, `GET /sessions/{id}`, `GET /sessions/{id}/next-pair`, `POST /sessions/{id}/comparisons/{position}`, com os schemas e as regras da seção 6.
  - **`MetaOptions`:** `{ segments: [{ city, purpose, price_floor, price_ceiling }] }`, com o menor e o maior preço de cada segmento.
  - **`POST /sessions`:** `target_pairs` vem de `PAIRS_DEMO`, `PAIRS_PRODUCT` ou `PAIRS_COLLECTION`, conforme `mode`. Em todos os modos, exige `city = "Goiânia"` e `purpose = "sale"` (senão, `422 validation_error`). Na coleta, também exige `consent = true` e grava `consent_at = now()`. O servidor gera `participant_code` como `P` mais o maior número já usado somado a 1, com dois dígitos no mínimo (P01, P02...), na mesma transação e depois de `pg_advisory_xact_lock`, para duas pessoas ao mesmo tempo não receberem o mesmo código. `SessionOut` não devolve o código. Quem trocar de aparelho abre outra sessão, com outro código.
  - **Pares da coleta:** os candidatos são `candidate_listings(session)` (seção 6), ordenados por `code`. A lista dos `target_pairs` pares é `random_pairs(len(candidatos), target_pairs, np.random.default_rng(seed_for(session.id, 0)))`, recalculada de forma determinística a cada chamada. O par da posição k é o k-ésimo da lista, gravado em `comparisons` com `selection = 'random'` na primeira vez que for pedido.
  - **Modos `demo` e `product`:** `POST /sessions` já funciona, mas `GET /next-pair` devolve `501 not_available` até a E10.
  - **Testes:** criação com e sem consentimento; códigos gerados em sequência (P01, P02); 422 fora de Goiânia ou de compra; os pares da coleta sem repetir; recarregar devolve o mesmo par pendente; 409 em resposta repetida e fora de ordem; 204 depois do último par e `status = done`; 404 com sessão inexistente; 422 com `price_min >= price_max`.
  - **Verificação:** `cd backend && uv run pytest -q tests/api`.
- [ ] **E08 · Telas da coleta** · qui 05/11 · depende de: E05, E07, M1 e M4 aprovados
  - **Arquivos:** `frontend/src/api/schema.d.ts` (gerado com `pnpm gen:api`), `src/api/client.ts` (`createClient<paths>({ baseUrl: "/api/v1" })`), `src/api/queries.ts`; `src/lib/format.ts` (`formatBRL`, `formatArea`, `formatDistance` ("2,3 km"), via `Intl.NumberFormat("pt-BR")`); `src/features/collection/*` e `src/features/compare/*`, com os componentes e arquivos listados em `m1-coleta.md` e `m4-comparar.md`; `src/mocks/handlers.ts`; os testes desses componentes; `src/app/router.tsx` (só trocar o placeholder de `/coleta`).
  - **Comportamento:** o de M1 e M4. Além disso: o tempo de resposta é medido com `performance.now()` desde que o par aparece; as teclas ← e → escolhem; os botões ficam desabilitados enquanto a resposta é enviada; ao receber `done: true`, mostra o agradecimento. O schema do formulário é o `collectionFormSchema` descrito em `m1-coleta.md`.
  - **Testes:** a tela inicial leva ao formulário; sem consentimento não envia; o `POST /sessions` envia Goiânia e `sale`; clique e tecla ← escolhem A; botão desabilitado durante o envio; resposta 204 leva ao agradecimento.
  - **Verificação:** `pnpm test:run && pnpm lint && pnpm typecheck`; e, com `make dev`, João completa 5 pares em uma janela de 375 px.
- [ ] **E09 · Docker completo, exportação e túnel** · qui 05/11, até 17h · depende de: E07, E08
  - **Arquivos:** `backend/Dockerfile`; `frontend/Dockerfile`; `frontend/nginx.conf`; `docker-compose.yml` (serviços `api` e `web` da seção 10); o comando `export` em `backend/app/cli.py`; `backend/app/services/export_service.py`; `backend/tests/services/test_export.py`; `README.md` (como rodar e o túnel).
  - **`backend/Dockerfile`:** `python:3.12-slim`; copiar o `uv` da imagem `ghcr.io/astral-sh/uv`; `WORKDIR /app`; `uv sync --frozen --no-dev`; `ENV PATH=/app/.venv/bin:$PATH`; `CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"`.
  - **`frontend/Dockerfile`:** estágio de build com `node:24-alpine` e `corepack enable`, `pnpm install --frozen-lockfile`, `pnpm build`; estágio final `nginx:alpine` com o `dist/` em `/usr/share/nginx/html`.
  - **`nginx.conf`:** `location /api/ { proxy_pass http://api:8000; }` e `location / { try_files $uri /index.html; }`. No bloco `server`, `access_log off;`, para o servidor não registrar o IP de quem responde à coleta, porque a tela inicial promete que nenhum dado pessoal é coletado.
  - **`export --out <arquivo>`:** grava JSON neste formato exato (lido pela A07):

  ```json
  {
    "exported_at": "2026-11-08T12:05:00-03:00",
    "feature_keys": ["log_price", "log_area", "...as 12 chaves"],
    "participants": [
      {
        "participant_code": "P01",
        "session_id": "uuid ou null",
        "persona_slug": "familia",
        "city": "Goiânia",
        "purpose": "sale",
        "center": [12 números],
        "scale": [12 números],
        "pairs": [
          {"position": 1, "left_code": "GYN-V-0012", "right_code": "GYN-V-0031",
           "t_left": [12 números], "t_right": [12 números], "chosen": "A", "response_ms": 2310}
        ]
      }
    ]
  }
  ```
  - **Regras do export:** só sessões `collection` com pelo menos 20 pares respondidos e mediana de `response_ms` desses pares de pelo menos 1.000 ms (abaixo disso, a pessoa não teve tempo de comparar os dois imóveis); cada sessão tem o próprio código; só pares respondidos, em ordem de `position`; `t_left` e `t_right` são as linhas de `raw_matrix` (antes da padronização); `center` e `scale` vêm de `feature_stats` do segmento.
  - **Verificação:** `make up` a partir de um clone limpo, seguido de `make seed`, sobe tudo; `curl http://localhost:8080/api/v1/health` responde ok; `make tunnel` gera um endereço, e um celular fora da rede local completa os 25 pares por ele; `make export` gera um JSON válido com esse participante. **João envia o link aos colegas às 18h**; o mesmo link serve para todos.

* [ ] **E10 · API do feed, do modelo e do experimento** · sex 06/11 · depende de: A06 concluída em `docs/STATUS.md`
  - **Arquivos:** `backend/app/services/posterior_service.py`, `feed_service.py`, `experiment_service.py`, `pair_service.py` (acrescentar o modo adaptativo); `backend/app/schemas/feed.py`, `posterior.py`, `experiment.py`; `backend/app/api/v1/__init__.py` (registrar as rotas novas), `feed.py`, `posterior.py`, `experiment.py`, `meta.py` (acrescentar `/meta/features` e `/meta/inspection-items`), `sessions.py` (acrescentar o recálculo depois da resposta); o comando `load-results` em `backend/app/cli.py`; testes em `backend/tests/api/` e `backend/tests/services/`.
  - **`posterior_service.get_or_fit(session, n) -> MCMCResult`:** se existir linha em `posteriors` com `(session_id, n_comparisons = n)`, carrega as amostras (`np.load` do `bytea`, convertido para `float64`) e devolve. Senão: D = z(vencedor) − z(perdedor) dos n primeiros pares respondidos, em ordem de `position`, com z = `standardize(raw_matrix(...), center, scale)` do segmento da sessão; `mu` e `sd` vêm de `personas.prior_mean` e `prior_sd`, na ordem de `FEATURE_KEYS`; `fit_posterior(D, mu, sd, seed_for(session.id, n), MCMCConfig(...))` com os valores de `MCMC_*` das configurações; grava a linha (amostras em `float32` com `np.save`, `mean`, `sd`, `ci_low` e `ci_high` por chave, campos de diagnóstico e `seed`) e devolve.
  - **Depois de cada resposta** (`POST /comparisons`), nos modos `demo` e `product`: chamar `get_or_fit(session, answered)` e devolver os diagnósticos em `AnswerOut`. No modo `collection`, não roda MCMC e devolve `diagnostics = null`.
  - **`GET /next-pair` nos modos `demo` e `product`:** candidatos de `candidate_listings`; `Z` padronizado; `samples = get_or_fit(session, answered).samples`; `shown` = conjunto de `frozenset({i, j})` dos pares já mostrados, em índices dos candidatos; `next_pair_bald(Z, samples, shown, np.random.default_rng(seed_for(session.id, 10_000 + answered)))`; gravar com `selection = 'adaptive'`. Com o corte C3, usar `random_pairs` como na coleta.
  - **`GET /sessions/{id}/feed?method=bayes|persona&at=N&limit=30&offset=0`:** `n = at` se informado, senão `answered`; `at` fora de 0..answered devolve 422. `bayes`: `samples` de `get_or_fit(session, n)`, `compute_affinity(Z, samples)` e `explain(Z[i], samples.mean(0))`. `persona`: `samples = mu[None, :]` e `reasons = []`. Cada `FeedItem`: `score = to_score(mean[i], 0)`, `affinity_pct = round(100 * mean[i], 1)`, `interval = (round(100 * p5[i], 1), round(100 * p95[i], 1))`, `inspection_delta = 0`, `rank` a partir de 1. Ordem e cache conforme a seção 6.
  - **`GET /sessions/{id}/posterior?n=`:** um `WeightOut` por chave, com `label` de `FEATURES`, priori da persona e média, desvio e percentis 5 e 95 das amostras; mais os diagnósticos. `n` padrão: `answered`.
  - **`GET /sessions/{id}/posterior/trace?feature=<chave>&n=`:** `TraceOut = { feature_key: str, chains: list[list[float]] }`, com `samples.reshape(n_chains, -1, 12)[:4, :, j]`. Chave fora de `FEATURE_KEYS` devolve 422.
  - **`GET /experiment/summary?run_id=`:** sem `run_id`, usa a rodada mais recente (maior `created_at`). Schemas:

  ```python
  class ExperimentRow(BaseModel):
      method: Literal["equal", "persona", "mle", "bayes"]; n_train: int
      acc_mean: float; acc_sd: float; ll_mean: float; ll_sd: float; n_participants: int
  class ParticipantRow(BaseModel):
      participant_code: str; method: str; acc_mean: float      # sempre n_train = 5
  class ExperimentSummary(BaseModel):
      run_id: UUID | None; simulated: bool; participants: int
      rows: list[ExperimentRow]; per_participant: list[ParticipantRow]
  ```

  `simulated` é verdadeiro se algum `participant_code` começar com "S". Sem resultados: `run_id = null` e listas vazias.
  - **`load-results <csv>`:** insere as linhas em `experiment_results`; se o `run_id` já existir, não faz nada e avisa.
  - **Testes:** feed com 0 e com 3 pares; `method=persona`; `at=0` diferente de `at=3`; `at` inválido dá 422; score sempre entre 0 e 100; segunda chamada do feed não roda o MCMC de novo (verificar com `unittest.mock`); posteriori com 12 pesos; traço com 4 cadeias de 250 pontos; resumo vazio e com um CSV de exemplo; demo com 3 pares sem repetir.
  - **Verificação:** `cd backend && uv run pytest -q && uv run ruff check .`.
* [ ] **E11 · Início, onboarding e modo demo** · sex 06/11 · depende de: G2, E08
  - **Arquivos:** `frontend/src/features/home/*`, `src/features/onboarding/*` e `src/features/demo/*`, com os componentes de `m2-inicio.md`, `m3-onboarding.md` e `m3b-demo.md`; seus testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx` (trocar os placeholders de `/`, `/comecar` e `/demo`).
  - **Comportamento:** o dos mockups e da seção 7 ("Onboarding"). Os schemas são `step1Schema` e `step2Schema` da seção 7. Ao enviar: `POST /sessions`, `setSession(id, mode)` e ir para `/comparar`. No modo demo, um toque na persona envia `mode = "demo"` com o `demo_defaults` dela. Sem `sessionId` válido, `/comparar`, `/feed` e `/modelo` redirecionam para `/comecar`.
  - **Testes:** mensagens de erro dos schemas; máximo menor que o mínimo não envia; um toque no modo demo chama `POST /sessions` com os `demo_defaults` certos.
  - **Verificação:** `pnpm test:run && pnpm lint && pnpm typecheck`.
* [ ] **E12 · Comparações da demo e feed com Antes e Depois** · sáb 07/11 · depende de: E10, E11
  - **Arquivos:** `src/features/compare/*` (só para aceitar os modos demo e produto); `src/features/feed/*`, com os componentes de `m5-feed.md`; seus testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.
  - **Comparações:** reaproveitar o componente de M4. Pré-carregar o próximo par com `queryClient.prefetchQuery` assim que a resposta for aceita. Ao terminar, ir para `/feed`. Depois de cada resposta, invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
  - **Feed:** seção 7 ("Feed"). Chaves de query `['feed', id, method, at]`. \[C2\] Os motivos aparecem como chips; com o corte C2, o cartão mostra só score e intervalo.
  - **Testes:** a alternância Antes e Depois troca a ordem renderizada; o selo mostra o número e a faixa de cor certa nos limites 39, 40, 69 e 70; os estados vazio e de erro mostram os textos de `copy.ts`.
  - **Verificação:** `pnpm test:run && pnpm lint && pnpm typecheck`; com `make dev`, o fluxo da demo completo funciona.
* [ ] **E13 · Painel do modelo** · sáb 07/11 · depende de: E10, G2
  - **Arquivos:** `src/features/model-panel/*`, com os componentes de `m6-modelo.md`; testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.
  - **Conteúdo:** gráfico de intervalos do Recharts (`ComposedChart` com `Scatter` e `ErrorBar`): por característica, um ponto para a média da priori e outro para a da posteriori, com a faixa de 5% a 95%. \[C4\] Traço: `LineChart` com as 4 cadeias do peso escolhido num `Select`. Quadro de diagnósticos (aceitação, R-hat, ESS, tempo), com a cor de alerta do tema quando `ok = false`.
  - **Testes:** renderiza 12 linhas de pesos com os dados do MSW; `ok = false` mostra o estado de alerta.
  - **Verificação:** `pnpm test:run && pnpm lint && pnpm typecheck`.
* [ ] **E14 · Painel do experimento** · sáb 07/11 · depende de: E10, G2
  - **Arquivos:** `src/features/experiment/*`, com os componentes de `m7-experimento.md`; testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.
  - **Conteúdo:** `LineChart` de `acc_mean` contra `n_train`, uma linha por método, com faixa de ±1 desvio (`Area`); tabela com acurácia e perda logarítmica; barras por participante em n\_train = 5; aviso fixo "Dados simulados" quando `simulated = true`; estado vazio quando `run_id = null`.
  - **Testes:** o aviso aparece com `simulated = true`; o estado vazio aparece sem resultados.
  - **Verificação:** `pnpm test:run && pnpm lint && pnpm typecheck`.
* [ ] **E15 · Qualidade, README e `make demo`** · dom 08/11 · depende de: E12 a E14 e as FIX da A-REV2
  - **Arquivos:** os apontados por cada `FIX-n`; `README.md` (requisitos: Docker, Node 24, pnpm, uv e cloudflared; `make up`, `make seed`, `make demo`, `make dev`, `make check`; coleta pelo túnel; solução de problemas: porta ocupada, banco vazio, imagens sem internet).
  - **Verificação:** `make check` passa por inteiro; um clone limpo roda `make demo` e abre o modo demo funcionando.
* [ ] **E16 · Correções e teste offline** · seg 09/11, até 18h · depende de: A09
  - **Arquivos:** só os apontados por cada `FIX-n` aberto pela A09.
  - **Verificação:** `make check` passa; João repete o roteiro manual da seção 9 sem falhas.
* [ ] **E17 · \[C1\] Detalhe do imóvel e vistoria** · seg 09/11, só com autorização de João às 12h e M8 aprovado · depende de: E16
  - **Arquivos:** `backend/app/api/v1/__init__.py` (registrar a rota nova), `listings.py`; `backend/app/services/inspection_service.py`; as rotas de vistoria em `sessions.py`; o cálculo de `inspection_delta` em `feed_service.py`; `src/features/listing/*`; testes.
  - **Conteúdo:** seções 6 e 7 ("Detalhe e vistoria"). O feed passa a somar a vistoria com `to_score(mean, soma dos delta)`.
  - **Verificação:** `make check`; marcar "Rua barulhenta" baixa o score na hora, e o valor persiste ao recarregar.

## 9. Testes, verificação e critérios de aceite

Cada tarefa traz seus próprios comandos de verificação (seção 8). Esta seção reúne o que vale para todas e o roteiro manual que substitui o teste automatizado de ponta a ponta.

**`make check`** é a porta de qualidade única. Roda no notebook antes de cada commit de fim de tarefa e no fim de cada dia:

```bash
cd backend && uv run ruff check . && uv run ruff format --check . \
  && uv run mypy app/engine && uv run pytest -q -m "not perf"
cd frontend && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run
```

| Camada | Dono | Ferramenta | O que cobrir |
| --- | --- | --- | --- |
| Motor (`app/engine`) | A | pytest | Todos os testes de A02, A03, A05, A06 e A07; cobertura de pelo menos 90% (`pytest --cov=app/engine`) |
| Serviços e API | E | pytest, `TestClient` e banco `imobscore_test` | Os testes listados em E06, E07, E09 e E10; cada rota com um caso de sucesso e um de erro |
| Telas | E | Vitest, Testing Library e MSW | Os testes listados em E08 e E11 a E14 |
| Ponta a ponta | J com A | Roteiro manual abaixo | Os 10 passos, offline |

**Convenções**

- Todo teste numérico usa semente fixa e tolerância explícita (`np.testing.assert_allclose(..., atol=...)`).
- O teste de desempenho do MCMC recebe `@pytest.mark.perf` e fica fora do `make check`. Claude o roda na A05 e na A-REV1.
- Nenhum teste depende de internet nem do horário.
- Nenhum agente apaga, pula ou afrouxa um teste para fazê-lo passar.

### Roteiro manual offline (A09 com João em 09/11; João repete em 10/11)

- [ ] 1\. Desligar o Wi-Fi. Rodar `make demo`. O modo demo abre em até 2 minutos.
- [ ] 2\. Tocar em Família. O primeiro par aparece em até 1 segundo.
- [ ] 3\. Responder 3 pares em menos de 20 segundos, sem espera visível entre eles.
- [ ] 4\. O feed aparece com 30 imóveis, selo, intervalo e motivos \[C2\]. Todo score fica entre 0 e 100.
- [ ] 5\. Alternar Antes e Depois: a lista reordena com animação.
- [ ] 6\. Painel do modelo: 12 pesos, R-hat abaixo de 1,05 e diagnóstico sem alerta.
- [ ] 7\. Painel do experimento: dados reais, ou o aviso "Dados simulados".
- [ ] 8\. Recarregar a página no meio dos pares: volta ao mesmo par, sem pular.
- [ ] 9\. Em 375 px (DevTools), a coleta e a demo funcionam sem rolagem horizontal.
- [ ] 10\. Na aba Network do navegador, nenhuma requisição sai de `localhost`.

### Critérios de aceite do MVP (09/11, 22h)

- [ ] `make check` passa por inteiro.
- [ ] Os 10 passos do roteiro manual passam.
- [ ] `docs/CHECKPOINTS.md` tem CP1 a CP7 com "Entendido: sim".
- [ ] `docs/mockups/APPROVAL.md` tem M1 a M7 aprovados, e as telas implementadas batem com eles.
- [ ] `docs/results.md` e `data/results/` existem, com dados reais ou simulados declarados.
- [ ] `docs/STATUS.md` sem `FIX-n` aberto e sem pergunta aberta.
- [ ] Tag `v1.0.0` criada.

## 10. Docker Compose, seed e demo offline

No dia, o notebook roda `make demo` sem internet e abre o navegador em `http://localhost:8080/demo`. Todas as imagens e dependências são baixadas antes, em casa.

```yaml
# docker-compose.yml (referência exata)
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: imobscore
      POSTGRES_PASSWORD: imobscore
      POSTGRES_DB: imobscore
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/initdb:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U imobscore"]
      interval: 3s
      retries: 20
    ports: ["5432:5432"]          # usado por make dev e pelos testes
  api:
    build: ./backend
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg://imobscore:imobscore@db:5432/imobscore
    volumes:
      - ./data:/app/data            # pares exportados e resultados ficam no repositório
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 5s
      retries: 20
  web:
    build: ./frontend
    ports: ["8080:80"]
    depends_on:
      api: { condition: service_healthy }
volumes:
  pgdata:
```

O serviço `db` publica a porta 5432 para `make dev` e para os testes. O `.env` local usa `DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore` e `TEST_DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore_test`. Os comandos `make` estão definidos na tarefa E01.

**Checklist da véspera (10/11)**

- [ ] Com internet: `docker compose pull` e `make up`, para deixar todas as imagens no cache do notebook.
- [ ] Desligar o Wi-Fi e repetir o roteiro manual da seção 9 a partir de `make reset` e `make demo`.
- [ ] Conferir que `data/collected/pairs.json` e `data/results/` estão no repositório. O `make demo` recarrega os resultados a partir deles, mesmo com o banco recriado.
- [ ] Desativar a suspensão de tela e as atualizações automáticas do sistema.
- [ ] Deixar um segundo navegador aberto no painel do experimento, ao lado da demo.
- [ ] Plano B: gravar um vídeo de 60 segundos da demo.
- [ ] Ler `docs/demo-script.md` em voz alta uma vez.

## 11. Fases 2 a 5 (nível macro)

As fases seguintes reaproveitam a mesma base (FastAPI, Postgres, React e o motor) e só começam quando o portão anterior é cumprido. Nada desta seção entra no MVP. Ela existe para o agente não tomar decisões agora que fechem esses caminhos depois.

| Fase | O que muda na arquitetura | Tecnologias candidatas | Portão para a próxima |
| --- | --- | --- | --- |
| 2 · Validação com quem procura imóvel | Deploy na nuvem; login; cadastro manual de anúncios reais de uma cidade; favoritos e visitas; teste A/B do feed contra a busca por filtros | Compose em uma VPS com Caddy (HTTPS) ou Render/Fly.io; Postgres gerenciado; login por link mágico no e-mail; PostHog (análise de uso); Sentry (erros); páginas de privacidade e exclusão de dados para a LGPD | As pessoas preferem o feed aos filtros? |
| 3 · Agregador de anúncios | Pipeline de ingestão fora da API: fila, workers e agendador; fonte e data de atualização em cada anúncio; deduplicação entre fontes | Workers com Dramatiq ou Celery + Redis; `lxml` para feeds XML de parceiros; `httpx` + `selectolax` e Playwright para importação por link; PostGIS e geocodificação; `rapidfuzz` e `imagehash` para deduplicar; coleta de portais só depois de análise jurídica | Volume suficiente para cobrir uma cidade? |
| 4 · Motor híbrido | Modelo global treinado com cliques e favoritos de todos os usuários; os pesos bayesianos individuais ficam por cima; exploração no feed | LightGBM com objetivo `lambdarank` (LambdaMART); PyTorch para MLP + RankNet; amostragem de Thompson usando as amostras do MCMC; MLflow para registrar experimentos; métricas NDCG@10 offline e teste A/B online | Tráfego e retenção que interessem a imobiliárias? |
| 5 · Monetização | Links de saída rastreados (custo por clique ou por contato qualificado); painel B2B multiempresa; cobrança | Redirecionador com registro de cliques e filtro de fraude; papéis e permissões por empresa; gateway de pagamento com PIX e boleto (Stripe, Pagar.me ou Asaas) | — |

**Decisões do MVP que preservam esses caminhos**

- O motor não conhece o banco nem HTTP. Na fase 4, ele vira a camada pessoal sem reescrita.
- `listings` já tem `code` único. Na fase 3, entram as colunas `source`, `source_url` e `source_updated_at`, e uma tabela de ligação para duplicatas.
- As sessões anônimas podem ser associadas a um usuário na fase 2 com uma coluna `user_id` anulável, sem perder o histórico.
- Tudo é configurado por variáveis de ambiente, então o mesmo Compose sobe em uma VPS.

## 12. Questões em aberto

O plano já assume uma resposta padrão para cada questão, então nada bloqueia o início em 04/11. João troca a resposta se quiser, até a data indicada, e Claude atualiza o plano.

| Questão | Padrão assumido | Alternativas | Decidir até |
| --- | --- | --- | --- |
| Quantas horas por dia João tem para checkpoints e aprovações? | 4 a 5 horas | Menos tempo: CP1 e CP2 viram um só, e CP5 vai para o domingo | qua 04/11, manhã |
| Qual modelo do OpenCode Go faz o papel de executor? | Qualquer um que João escolher; o plano não depende do modelo | Trocar de modelo se uma tarefa falhar duas vezes | qua 04/11, manhã |
| Como os colegas acessam a coleta? | Túnel do Cloudflare com o notebook ligado de 05/11, 18h, a 08/11, 12h | Coleta presencial no notebook; deploy mínimo só da coleta | qui 05/11, 12h |
| Quantos colegas e quantos pares cada um? | Até 10 colegas, 20 pares aleatórios (cerca de 5 minutos), o que limita a curva a n\_train = 10, com 10 pares de teste; catálogo inteiro em Goiânia e à venda. Decidido por João em 04/11; de 25 para 20 pares em 05/11, depois das primeiras respostas | — | Decidido |
| As 12 características da seção 5.1 estão certas? | Lista da seção 5.1 | Trocar `is_house` por andar; separar o condomínio do preço | qua 04/11, antes da A02 |
| Os pesos das personas fazem sentido? | Tabela da seção 5.3 | Ajuste na A-REV2, olhando o feed de cada persona | sáb 07/11 |
| Formato do relatório para a disciplina | `docs/results.md`, figuras e CSV gerados pela A07 e pela A08 | Confirmar com o professor | sex 06/11 |
| Reverter o corte C1 (vistoria)? | Não | Sim, se tudo estiver verde em 09/11 às 12h | seg 09/11, 12h |
