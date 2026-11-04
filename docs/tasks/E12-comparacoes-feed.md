# E12 · Comparações da demo e feed com Antes e Depois

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sáb 07/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Completar as comparações da demo e implementar o feed com a alternância Antes e Depois.

## Arquivos permitidos

`src/features/compare/*` (só para aceitar os modos demo e produto); `src/features/feed/*`, com os componentes de `m5-feed.md`; seus testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.

## Dependências

E10, E11

## Especificação

- **Comparações:** reaproveitar o componente de M4. Pré-carregar o próximo par com `queryClient.prefetchQuery` assim que a resposta for aceita. Ao terminar, ir para `/feed`. Depois de cada resposta, invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
- **Feed:** seção 7 ("Feed"). Chaves de query `['feed', id, method, at]`. \[C2\] Os motivos aparecem como chips; com o corte C2, o cartão mostra só score e intervalo.
- **Testes:** a alternância Antes e Depois troca a ordem renderizada; o selo mostra o número e a faixa de cor certa nos limites 39, 40, 69 e 70; os estados vazio e de erro mostram os textos de `copy.ts`.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`; com `make dev`, o fluxo da demo completo funciona.
