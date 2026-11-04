# M6 · Painel do modelo
Rota: /modelo   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Mostrar quanto cada característica pesa para a pessoa, quanto as escolhas mudaram isso e se o MCMC convergiu, em linguagem que um leigo entenda e a banca possa cobrar.

## Layout (celular e notebook)

**Comum:** `PageHeader active="model"`, título, resumo e três painéis em cartão, nesta ordem: pesos, diagnósticos e traço. Largura de `max-w-5xl`.

**Celular:** rótulos do gráfico de pesos em coluna de 134 px; diagnósticos em duas colunas; traço com 200 px de altura; "Catálogo de demonstração" em uma linha no fim da página.

**Notebook:** rótulos do gráfico em coluna de 170 px; diagnósticos em quatro colunas; `Select` do traço com `w-72`.

**Gráfico de pesos:** uma linha por característica, na ordem de `FEATURE_KEYS`, com eixo de −3 a 3 e linha do zero destacada. Em cada linha, duas marcas: a da posteriori acima e a da priori abaixo, cada uma com um ponto na média e uma barra de 2 px de 5% a 95%. Valores fora do eixo ficam no limite.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `ModelPanelPage` | `src/features/model-panel/model-panel-page.tsx` | nenhuma | `Card`, `Skeleton` |
| `WeightsChart` | `src/features/model-panel/weights-chart.tsx` | `weights: WeightOut[]`, `priorOnly: boolean` | Recharts: `ComposedChart`, `Scatter`, `ErrorBar`, `XAxis`, `YAxis`, `ReferenceLine`, `Tooltip` |
| `WeightsTable` | `src/features/model-panel/weights-table.tsx` | `weights: WeightOut[]` | nenhum: `<details>` e `<table>` |
| `DiagnosticsBoard` | `src/features/model-panel/diagnostics-board.tsx` | `diagnostics: Diagnostics` | `Card` |
| `TraceChart` | `src/features/model-panel/trace-chart.tsx` | `sessionId: string`, `n: number`, `features: FeatureOut[]` | `Select`; Recharts: `LineChart`, `Line`, `XAxis`, `YAxis`, `Tooltip` |
| `ModelMessage` | `src/features/model-panel/model-message.tsx` | `onRetry: () => void` | `Button` |

Cores das séries: posteriori `var(--chart-1)`, priori `var(--chart-2)`; cadeias de 1 a 4, `var(--chart-1)` a `var(--chart-4)`. Pontos com raio 4 e contorno de 2 px na cor do cartão; linhas de 2 px no gráfico de pesos e de 1,25 px no traço; grade em `var(--border)`. Textos usam as cores de texto, nunca a cor da série. Sempre há legenda.

Ícones de `lucide-react`: `CircleCheck`, `TriangleAlert`, `ChevronDown`, `RefreshCw`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `WeightOut.label` | Rótulo da linha | Texto da API |
| `prior_mean`, `post_mean`, `ci_low`, `ci_high` | Gráfico e tabela; a tabela usa `copy.modelPanel.weights.interval` | Duas casas, com `Intl.NumberFormat("pt-BR")` |
| `prior_sd` | Faixa da priori: `prior_mean ± 1,645 × prior_sd` | — |
| `Diagnostics.accept_rate` | Aceitação | Porcentagem inteira |
| `rhat_max` | R-hat | Duas casas |
| `ess_min` | ESS | Inteiro |
| `elapsed_ms` | Tempo | `copy.modelPanel.diagnostics.timeValue(ms)` |
| `ok` | Mensagem geral e alerta | `copy.modelPanel.diagnostics.ok` ou `.alert` |
| `TraceOut.chains` | Linhas do traço | — |
| `FeatureOut.key`, `label` | Opções do `Select`; padrão `dist_center` | Texto da API |
| `SessionOut.persona_slug` + `PersonaOut.name`, `SessionOut.answered` | Resumo | `copy.feed.summary(name, answered)` |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Normal | `answered > 0` e `ok = true` | `modelPanel.*` |
| Alerta | `ok = false` | `modelPanel.diagnostics.alert`, com `TriangleAlert`; não bloqueia nada |
| Sem escolhas | `answered = 0` | Só o painel de pesos, com `priorOnly` e `modelPanel.weights.priorOnlyLead` |
| Carregando | `GET /posterior` em andamento | Dois `Skeleton`; `modelPanel.loading` só para leitores de tela |
| Erro | Falha em `GET /posterior` | `modelPanel.loadError.*`, botão `common.retry` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Busca a posteriori atual | `GET /sessions/{id}/posterior`; `['posterior', id, n]` |
| Trocar o peso no `Select` | Busca o traço desse peso | `GET /sessions/{id}/posterior/trace?feature=...&n=...`; `['trace', id, n, feature]` |
| Hover ou foco em uma marca | Tooltip com rótulo, média e faixa | — |
| Abrir "Ver como tabela" | Mostra os 12 pesos em tabela | — |
| Botão "Tentar de novo" | Refaz a consulta | `['posterior', id, n]` |

Sem `sessionId` válido, a rota redireciona para `/comecar`. **\[C4\]** Com o corte C4, o painel do traço sai.

## Textos (chaves de copy.ts usadas nesta tela)
`common.nav.*`, `common.appName`, `common.demoCatalog`, `common.retry`; `feed.summary`; `modelPanel.*`.

## Critérios de aceite visual (lista verificável)
- [ ] O gráfico mostra as 12 características, com priori e posteriori distinguíveis também pela posição na linha.
- [ ] A linha do zero se destaca da grade.
- [ ] Cada diagnóstico tem valor e uma frase para leigos, entre elas "Perto de 1: as cadeias concordam."
- [ ] `ok = false` mostra o alerta com ícone e texto.
- [ ] Existe uma tabela com os mesmos valores do gráfico.
- [ ] Os gráficos têm legenda, e os textos não usam a cor das séries.
- [ ] Em 375 px, não há rolagem horizontal, e os rótulos não invadem o gráfico.
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
