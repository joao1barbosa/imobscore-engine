# E08 · Telas da coleta

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qui 05/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar as telas da coleta a partir dos mockups aprovados M1 e M4.

## Arquivos permitidos

`frontend/src/api/schema.d.ts` (gerado com `pnpm gen:api`), `src/api/client.ts` (`createClient<paths>({ baseUrl: "/api/v1" })`), `src/api/queries.ts`; `src/lib/format.ts` (`formatBRL`, `formatArea`, `formatRent` com "/mês", via `Intl.NumberFormat("pt-BR")`); `src/features/collection/*` e `src/features/compare/*`, com os componentes e arquivos listados em `m1-coleta.md` e `m4-comparar.md`; `src/mocks/handlers.ts`; os testes desses componentes; `src/app/router.tsx` (só trocar o placeholder de `/coleta`).

## Dependências

E05, E07, M1 e M4 aprovados

## Especificação

- **Comportamento:** o de M1 e M4. Além disso: o tempo de resposta é medido com `performance.now()` desde que o par aparece; as teclas ← e → escolhem; os botões ficam desabilitados enquanto a resposta é enviada; ao receber `done: true`, mostra o agradecimento. O schema do formulário é o `collectionSchema` da seção 7 somado ao `step1Schema` e ao `step2Schema`.
- **Testes:** código inválido mostra a mensagem de `copy.ts`; sem consentimento não envia; clique e tecla ← escolhem A; botão desabilitado durante o envio; resposta 204 leva ao agradecimento.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`; e, com `make dev`, João completa 5 pares em uma janela de 375 px.
