# M5 · Feed
Rota: /feed   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Mostrar o ranking de afinidade com sua incerteza e, ao alternar Antes e Depois, fazer o visitante ver os imóveis trocando de lugar por causa das suas escolhas.

## Layout (celular e notebook)

**Comum:** `PageHeader active="feed"`, título, resumo, alternância Antes e Depois com a frase de explicação, lista de até 30 imóveis e o botão para `/modelo`. Largura de `max-w-3xl`. Não há link para o detalhe enquanto o corte C1 valer.

**Celular:** alternância com largura total e a frase abaixo dela; cartão sem ilustração, com o selo à direita, em coluna de `w-20`; "Catálogo de demonstração" em uma linha no fim da página.

**Notebook:** alternância à esquerda e frase à direita; cartão com ilustração de `size-24` à esquerda, dados no centro e selo à direita.

**Dentro do cartão, nesta ordem:** posição e mudança de posição, preço, título, bairro · cidade, os sete dados do imóvel e, só em Depois, até 4 motivos.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `FeedPage` | `src/features/feed/feed-page.tsx` | nenhuma | `Button`, `Skeleton` |
| `BeforeAfterToggle` | `src/features/feed/before-after-toggle.tsx` | `value: "before" \| "after"`, `onChange: (v: "before" \| "after") => void` | `Tabs` |
| `FeedCard` | `src/features/feed/feed-card.tsx` | `item: FeedItem`, `showReasons: boolean`, `previousRank: number \| null \| undefined` | `Card`, `Badge` |
| `ScoreBadge` | `src/features/feed/score-badge.tsx` | `score: number`, `low: number`, `high: number` | `Tooltip` |
| `RankChange` | `src/features/feed/rank-change.tsx` | `rank: number`, `previousRank: number \| null` | nenhum |
| `FeedMessage` | `src/features/feed/feed-message.tsx` | `tone: "empty" \| "error"`, `onRetry?: () => void` | `Button` |

Reaproveite do cartão de M4 os textos e os ícones dos dados do imóvel. Ícones de `lucide-react`: `Ruler`, `BedDouble`, `Bath`, `CarFront`, `CalendarDays`, `Dumbbell`, `MapPin`, `ArrowUp`, `ArrowDown`, `Sparkles`, `Plus`, `Minus`, `Info`, `ChartNoAxesColumn`, `SearchX`, `TriangleAlert`, `RefreshCw`.

**Selo (`ScoreBadge`):** círculo com o número sempre visível, em `text-score-foreground`. Fundo por faixa: `bg-score-low` de 0 a 39, `bg-score-mid` de 40 a 69 e `bg-score-high` de 70 a 100.

**Animação:** `motion.li` com `layout` e `key = listing.id`, 500 ms. Itens que entram ou saem da lista usam `AnimatePresence`. Com `prefers-reduced-motion`, a troca não anima.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `FeedItem.rank` | Posição | `copy.feed.rank(rank)` |
| `rank` na lista `at=0` | `previousRank` de `RankChange`; só em Depois | `copy.feed.movedUp`, `movedDown`, `kept`; `null` (fora dos 30): `copy.feed.enteredTop` |
| `score` | Selo | Número inteiro |
| `score` | Tooltip e `aria-label` do selo | `copy.feed.scoreTooltip(score)` |
| `interval` | Abaixo do selo | `copy.feed.interval(Math.round(low), Math.round(high))` |
| `reasons[].text` | Chips; `contribution > 0` usa `Plus` e `bg-secondary`, senão `Minus` e borda | Texto da API |
| `listing.price_brl` | Preço | `formatBRL` |
| `listing.title`, `neighborhood`, `city` | Título e local | `copy.compare.listing.location` |
| `listing.area_m2` | Dados | `formatArea` |
| `listing.bedrooms`, `bathrooms`, `parking`, `age_years`, `leisure_count` | Dados | `copy.compare.listing.*` |
| `listing.dist_center_km` | Dados | `copy.compare.listing.distCenter(formatDistance(km))` |
| `listing.illustration`, `kind` | Ilustração, só no notebook | `copy.compare.listing.illustrationAlt[kind]` |
| `SessionOut.persona_slug` + `PersonaOut.name`, `SessionOut.answered` | Resumo | `copy.feed.summary(name, answered)` |

Mesmo com `reasons` preenchido em `at=0`, os motivos só aparecem em Depois.

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Depois | Padrão, com `answered > 0` | `feed.afterHint(answered)`, cartões com motivos e `RankChange` |
| Antes | Alternância em Antes | `feed.beforeHint`, cartões sem motivos |
| Sem escolhas | `answered = 0` | Sem alternância; aviso com `feed.noPairsHint`; a lista de `at=0` |
| Carregando | Qualquer uma das duas consultas em andamento | Três `Skeleton`, sem alternância; `feed.loading` só para leitores de tela |
| Vazio | `items` vazio | `feed.empty.title`, `feed.empty.description`, link `feed.empty.action` para `/comecar` |
| Erro | Falha na consulta | `feed.loadError.*`, botão `common.retry` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Busca as duas listas, para a troca ser imediata | `GET /sessions/{id}/feed?at=0&limit=30`, `?at={answered}&limit=30`; `['feed', id, 'bayes', 0]`, `['feed', id, 'bayes', answered]` |
| Clicar em Antes ou Depois | Reordena com animação, sem nova consulta | — |
| Foco ou hover no selo | Mostra `feed.scoreTooltip` | — |
| Botão "Ver o que o modelo aprendeu" | Vai para `/modelo` | — |
| Link "Começar de novo" | Vai para `/comecar` | — |
| Botão "Tentar de novo" | Refaz as consultas | `['feed', id, 'bayes', n]` |

Sem `sessionId` válido, a rota redireciona para `/comecar`.

## Textos (chaves de copy.ts usadas nesta tela)
`common.nav.*`, `common.appName`, `common.demoCatalog`, `common.retry`; `feed.*`; `compare.listing.*`.

## Critérios de aceite visual (lista verificável)
- [ ] Alternar Antes e Depois anima os cartões para as novas posições, sem recarregar a lista.
- [ ] O selo sempre mostra o número, e os limites 39, 40, 69 e 70 caem na faixa de cor certa.
- [ ] O tooltip do selo diz "{score}% de chance de você preferir este a um imóvel típico" e abre também com o teclado.
- [ ] Abaixo do selo aparece "entre X e Y", sem quebrar a linha de forma a separar o número.
- [ ] Depois mostra no máximo 4 motivos, e os negativos têm o ícone `Minus`, não só outra cor.
- [ ] Antes não mostra motivos nem mudança de posição.
- [ ] Em 375 px, não há rolagem horizontal, e "Catálogo de demonstração" aparece na página.
- [ ] Em 1280 px, o cartão tem a ilustração à esquerda.
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
