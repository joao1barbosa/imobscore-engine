# E13 · Painel do modelo

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sáb 07/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar o painel do modelo: pesos, intervalos, traço das cadeias e diagnósticos.

## Arquivos permitidos

`src/features/model-panel/*`, com os componentes de `m6-modelo.md`; testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.

## Dependências

E10, G2

## Especificação

- **Conteúdo:** gráfico de intervalos do Recharts (`ComposedChart` com `Scatter` e `ErrorBar`): por característica, um ponto para a média da priori e outro para a da posteriori, com a faixa de 5% a 95%. \[C4\] Traço: `LineChart` com as 4 cadeias do peso escolhido num `Select`. Quadro de diagnósticos (aceitação, R-hat, ESS, tempo), com a cor de alerta do tema quando `ok = false`.
- **Testes:** renderiza 12 linhas de pesos com os dados do MSW; `ok = false` mostra o estado de alerta.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`.
