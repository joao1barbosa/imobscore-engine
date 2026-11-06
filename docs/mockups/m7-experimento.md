# M7 · Painel do experimento
Rota: /experimento   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Mostrar qual método acerta mais em pares nunca vistos, por número de escolhas e por participante, deixando claro quando os dados são simulados.

## Layout (celular e notebook)

**Comum:** `PageHeader active="experiment"`, título, frase de apoio, aviso de dados simulados quando houver, texto sobre o método e três painéis: curva, tabela e participantes. Largura de `max-w-5xl`. A rota não exige sessão.

**Celular:** curva com 240 px de altura; tabela com rolagem horizontal dentro do próprio painel; "Catálogo de demonstração" em uma linha no fim da página.

**Notebook:** curva com 320 px de altura; tabela sem rolagem.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `ExperimentPage` | `src/features/experiment/experiment-page.tsx` | nenhuma | `Card`, `Skeleton` |
| `AccuracyChart` | `src/features/experiment/accuracy-chart.tsx` | `rows: ExperimentRow[]` | Recharts: `ComposedChart`, `Line`, `Area`, `XAxis`, `YAxis`, `Tooltip` |
| `ResultsTable` | `src/features/experiment/results-table.tsx` | `rows: ExperimentRow[]` | nenhum: `<table>` |
| `ParticipantBars` | `src/features/experiment/participant-bars.tsx` | `rows: ParticipantRow[]` | Recharts: `BarChart` com `layout="vertical"`, `Bar`, `XAxis`, `YAxis`, `Tooltip` |
| `MethodLegend` | `src/features/experiment/method-legend.tsx` | nenhuma | nenhum |
| `ExperimentMessage` | `src/features/experiment/experiment-message.tsx` | `tone: "empty" \| "error"`, `onRetry?: () => void` | `Button` |

Cores fixas por método, em todo gráfico: `bayes` `var(--chart-1)`, `mle` `var(--chart-2)`, `persona` `var(--chart-3)`, `equal` `var(--chart-4)`. Na curva: linhas de 2 px, pontos de raio 4 com contorno de 2 px na cor do cartão, faixa de ±1 desvio com 10% de opacidade, eixo Y de 40% a 90% e grade em `var(--border)`. Nas barras: 7 px de espessura, ponta arredondada e 2 px entre as barras do mesmo participante. Textos usam as cores de texto, nunca a cor da série. Sempre há legenda. Os métodos não têm rótulo na ponta da linha, porque eles podem se sobrepor: a legenda e a tabela identificam cada um.

Ícones de `lucide-react`: `TriangleAlert`, `FlaskConical`, `RefreshCw`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `ExperimentSummary.simulated` | Aviso `experiment.simulated` | — |
| `participants` | Texto sobre o método | `copy.experiment.how(n)` |
| `rows[].method` | Série e linha da tabela | `copy.experiment.methods[method]` |
| `rows[].n_train` | Eixo X (3, 5, 10) e colunas da tabela | `copy.experiment.table.pairs(n)` |
| `rows[].acc_mean`, `acc_sd` | Linha e faixa; tabela | Porcentagem inteira |
| `rows[].ll_mean` | Tabela | Duas casas, com `Intl.NumberFormat("pt-BR")` |
| `per_participant[].participant_code`, `method`, `acc_mean` | Barras | Código; porcentagem inteira |
| `run_id` | `null` leva ao estado vazio | — |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Normal | `run_id` preenchido e `simulated = false` | `experiment.*` |
| Dados simulados | `simulated = true` | Normal, mais o aviso fixo `experiment.simulated`, com `TriangleAlert`, acima de tudo |
| Vazio | `run_id = null` | `experiment.empty.*` |
| Carregando | `GET /experiment/summary` em andamento | Dois `Skeleton`; `experiment.loading` só para leitores de tela |
| Erro | Falha na consulta | `experiment.loadError.*`, botão `common.retry` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Busca a rodada mais recente | `GET /experiment/summary`; `['experiment', 'latest']` |
| Hover ou foco em um ponto ou barra | Tooltip com método, pares e valor | — |
| Botão "Tentar de novo" | Refaz a consulta | `['experiment', 'latest']` |

## Textos (chaves de copy.ts usadas nesta tela)
`common.nav.*`, `common.appName`, `common.demoCatalog`, `common.retry`; `experiment.*`.

## Critérios de aceite visual (lista verificável)
- [ ] O eixo X da curva tem 3, 5 e 10 pares, sem 15, 20 ou 25.
- [ ] Cada método mantém a mesma cor na curva e nas barras, com legenda nos dois gráficos.
- [ ] `simulated = true` mostra o aviso no topo, com ícone e texto.
- [ ] `run_id = null` mostra o estado vazio, sem gráficos.
- [ ] A tabela traz acurácia e perda logarítmica de cada método em cada número de pares.
- [ ] Em 375 px, a página não tem rolagem horizontal; só a tabela rola dentro do painel.
- [ ] Os textos não usam a cor das séries.
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
