# E11 · Início, onboarding e modo demo

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sex 06/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar as telas de início, onboarding e modo demo a partir dos mockups aprovados.

## Arquivos permitidos

`frontend/src/features/home/*`, `src/features/onboarding/*` e `src/features/demo/*`, com os componentes de `m2-inicio.md`, `m3-onboarding.md` e `m3b-demo.md`; seus testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx` (trocar os placeholders de `/`, `/comecar` e `/demo`).

## Dependências

G2, E08

## Especificação

- **Comportamento:** o dos mockups e da seção 7 ("Onboarding"). Os schemas são `step1Schema` e `step2Schema` da seção 7. Ao enviar: `POST /sessions`, `setSession(id, mode)` e ir para `/comparar`. No modo demo, um toque na persona envia `mode = "demo"` com o `demo_defaults` dela. Sem `sessionId` válido, `/comparar`, `/feed` e `/modelo` redirecionam para `/comecar`.
- **Testes:** mensagens de erro dos schemas; máximo menor que o mínimo não envia; um toque no modo demo chama `POST /sessions` com os `demo_defaults` certos.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`.
