# E14 · Painel do experimento

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sáb 07/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar o painel do experimento: curvas de acurácia, tabela e barras por participante.

## Arquivos permitidos

`src/features/experiment/*`, com os componentes de `m7-experimento.md`; testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.

## Dependências

E10, G2

## Especificação

- **Conteúdo:** `LineChart` de `acc_mean` contra `n_train`, uma linha por método, com faixa de ±1 desvio (`Area`); tabela com acurácia e perda logarítmica; barras por participante em n\_train = 5; aviso fixo "Dados simulados" quando `simulated = true`; estado vazio quando `run_id = null`.
- **Testes:** o aviso aparece com `simulated = true`; o estado vazio aparece sem resultados.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`.
