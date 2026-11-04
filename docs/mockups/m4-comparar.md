# M4 · Comparação de um par
Rota: /comparar (demo, E12) e dentro de /coleta (E08)   Versão: 2   Status: ver APPROVAL.md

## Objetivo (1 frase)
Fazer a pessoa escolher entre dois imóveis em poucos segundos, com tudo o que importa à vista e sem precisar rolar a tela.

## Layout (celular e notebook)

O componente de M4 é o mesmo nas duas rotas. Quem o usa passa `sessionId` e `onDone`.

**Comum:** cabeçalho com "ImobScore" à esquerda e o selo "Catálogo de demonstração" à direita, sempre com fundo `bg-card` e `border-b`. Depois, nesta ordem: progresso, pergunta com a dica, os dois cartões e, no notebook, a dica de teclado. Largura máxima de `max-w-5xl`, centralizada.

**Celular (até 767 px, abaixo do breakpoint `md`):**
- Margens `px-4 py-3`; intervalo `gap-3`.
- Cartões empilhados, com o A em cima. Cada cartão é horizontal: ilustração de 80 × 80 px à esquerda e dados à direita.
- O segundo cartão termina dentro dos 667 px de altura, sem rolagem, no caso mais longo do mockup.
- Teclas e dica de teclado ficam ocultas.

**Notebook (a partir de `md`):**
- Margens `py-8`; intervalo `gap-6`.
- Dois cartões em `grid-cols-2`, com o A à esquerda.
- Cada cartão é vertical: faixa de ilustração de `h-44`, com `bg-accent` e `p-6`, e dados em `p-5` abaixo.
- Tecla `←` ou `→` no canto superior direito do cartão correspondente.

**Dentro do cartão, nesta ordem:** preço (maior elemento: `text-xl` no celular, `text-2xl` no notebook, `font-semibold`), título, bairro · cidade, grade de 2 colunas com área, quartos, banheiros, vagas, idade e lazer, a distância ao centro em uma linha inteira (`col-span-2`) e os selos.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `ComparePanel` | `src/features/compare/compare-panel.tsx` | `sessionId: string`, `onDone: () => void` | `Progress`, `Skeleton`, `Button`, `Sonner` |
| `ListingChoiceCard` | `src/features/compare/listing-choice-card.tsx` | `listing: ListingCard`, `shortcut: "←" \| "→"`, `disabled: boolean`, `state: "idle" \| "chosen" \| "dimmed"`, `onChoose: () => void` | Nenhum: é um `<button>` com as classes do mockup |
| `CompareSkeleton` | `src/features/compare/compare-skeleton.tsx` | nenhuma | `Skeleton` |
| `CompareMessage` | `src/features/compare/compare-message.tsx` | `tone: "done" \| "error"`, `title: string`, `description: string`, `onRetry?: () => void` | `Button` |

`ListingCard` é o tipo gerado de `src/api/schema.d.ts`. Ícones de `lucide-react`: `Ruler`, `BedDouble`, `Bath`, `CarFront`, `CalendarDays`, `Dumbbell`, `MapPin`, `PawPrint`, `ShieldCheck`, `Check`, `LoaderCircle`, `TriangleAlert`, `CircleCheck`, `RefreshCw`. A ilustração é `<img src="/illustrations/{listing.illustration}.svg">`, com `alt` conforme `kind`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `PairOut.position`, `PairOut.total` | Progresso e `value` da barra (`position - 1` de `total`) | `copy.compare.progress(position, total)` |
| `listing_a`, `listing_b` | Cartões da esquerda e da direita; "A" e "B" em `AnswerIn.chosen` | — |
| `price_brl` e `purpose` | Preço | `formatBRL` para `sale`; `formatRent` para `rent` |
| `title` | Título | Texto da API |
| `neighborhood`, `city` | Abaixo do título | `copy.compare.listing.location(neighborhood, city)` |
| `area_m2` | Grade | `formatArea` |
| `bedrooms` | Grade | `copy.compare.listing.bedrooms(n)` |
| `bathrooms` | Grade | `copy.compare.listing.bathrooms(n)` |
| `parking` | Grade | `copy.compare.listing.parking(n)` |
| `age_years` | Grade | `copy.compare.listing.age(n)` |
| `leisure_count` | Grade | `copy.compare.listing.leisure(n)` |
| `dist_center_km` | Grade, em linha inteira | `copy.compare.listing.distCenter(formatDistance(km))` |
| `pet_friendly` | Selo, só quando `true` | `copy.compare.listing.petFriendly` |
| `doorman_24h` | Selo, só quando `true` | `copy.compare.listing.doorman` |
| `illustration`, `kind` | Ilustração e `alt` | `copy.compare.listing.illustrationAlt[kind]` |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Normal | `GET /next-pair` devolveu um par | `compare.question`, `compare.hint`, `compare.progress`, cartões |
| Carregando | Consulta do par em andamento | Dois `CompareSkeleton`; `compare.loading` só para leitores de tela |
| Enviando | Depois da escolha, até a resposta do `POST` | Cartão escolhido com `ring-2 ring-primary` e ícone `Check`; o outro com `opacity-50`; ambos desabilitados; `compare.sending` |
| Vazio | `GET /next-pair` devolveu `204` | `compare.empty.title`, `compare.empty.description`, e chama `onDone` em seguida |
| Erro ao carregar | Falha no `GET /next-pair` | `compare.loadError.title`, `compare.loadError.description`, botão `common.retry` |
| Erro ao responder | Falha no `POST`, fora os casos abaixo | Aviso com `compare.answerError`; cartões habilitados de novo; o mesmo par continua |
| Sessão não encontrada | `404 session_not_found` | `common.apiErrors.session_not_found` e limpa a sessão com `reset()`; `/coleta` volta ao formulário e `/comparar` vai para `/comecar` |

Respostas `409` não são erro para a pessoa: `pair_already_answered` e `pair_out_of_order` buscam o par de novo em silêncio; `session_done` chama `onDone`.

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Busca o par pendente ou o próximo; recarregar a página não pula pares | `GET /sessions/{id}/next-pair`; `['pair', id]` |
| Par aparece | Começa a medir com `performance.now()`, uma vez por par | — |
| Tocar ou clicar no cartão esquerdo, ou tecla ← | Escolhe A | `POST /sessions/{id}/comparisons/{position}` com `{ chosen: "A", response_ms }` |
| Tocar ou clicar no cartão direito, ou tecla → | Escolhe B | Mesmo endpoint, com `{ chosen: "B", response_ms }` |
| Toque ou tecla durante o envio | Ignorado, sem segundo envio | — |
| Resposta com `done: false` | O cartão escolhido sai com `AnimatePresence` em até 200 ms e entra o próximo par | Atualiza `['pair', id]` |
| Resposta com `done: true`, ou `204` no `GET` | Chama `onDone`: agradecimento na coleta, `/feed` na demo | `['session', id]` |
| Botão "Tentar de novo" | Refaz a consulta | `['pair', id]` |

Com `prefers-reduced-motion`, a troca de par não tem animação. As setas só valem quando o foco não estiver em um campo de texto.

## Textos (chaves de copy.ts usadas nesta tela)
`common.appName`, `common.demoCatalog`, `common.retry`, `common.apiErrors.session_not_found`; `compare.question`, `compare.hint`, `compare.progress`, `compare.loading`, `compare.sending`, `compare.keyboardHint`, `compare.keyLeft`, `compare.keyRight`, `compare.chooseLabel`, `compare.empty.*`, `compare.loadError.*`, `compare.answerError`, `compare.listing.*`.

## Critérios de aceite visual (lista verificável)
- [ ] Em 375 × 667 px, os dois cartões cabem sem rolagem no maior par do mockup, sem rolagem horizontal.
- [ ] Em 1280 px, os cartões ficam lado a lado, com a mesma altura, e a tecla de cada um aparece no canto superior direito.
- [ ] O preço é o maior texto do cartão, e o aluguel sempre traz "/mês".
- [ ] O cartão inteiro é um único `<button>`, com `aria-label` de `compare.chooseLabel` e foco visível.
- [ ] Área, quartos, banheiros, vagas, idade, lazer e distância sempre têm texto, não só ícone.
- [ ] "Aceita pet" e "Portaria 24 h" aparecem só quando o campo é `true`.
- [ ] A barra de progresso está em `aria-live="polite"` e mostra `Par 12 de 25` com 11 de 25 preenchidos.
- [ ] Enviando: o cartão escolhido tem anel e ícone, o outro fica esmaecido, e um segundo clique não gera outro `POST`.
- [ ] Nenhum texto visível está escrito direto no componente: todos vêm de `copy.ts` ou da API.
- [ ] As cores vêm só das variáveis de `theme.css`, nos temas claro e escuro.
