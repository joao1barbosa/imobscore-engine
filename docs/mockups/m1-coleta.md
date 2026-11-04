# M1 · Coleta
Rota: /coleta   Versão: 2   Status: ver APPROVAL.md

## Objetivo (1 frase)
Levar um colega do link ao fim dos 25 pares, sabendo do que se trata, com consentimento registrado e sem digitar nenhum dado pessoal.

## Layout (celular e notebook)

Uma única rota com quatro etapas, nesta ordem: tela inicial, formulário, pares (componente de M4, ver `m4-comparar.md`) e agradecimento.

**Comum:** o mesmo cabeçalho de M4. Coluna única de `max-w-2xl`, centralizada.

**Tela inicial:** título, frase de abertura, três cartões ("O que você vai fazer", "Como usamos suas respostas" e "Nenhum dado pessoal"), cada um com ícone à esquerda, e o botão "Quero participar".

**Formulário:** uma só página, com título, frase e três seções em cartão: "Sua participação" (consentimento), "O que você procuraria" (aviso fixo de Goiânia e compra, mais a faixa de preço) e "Qual perfil mais parece com você?". O botão de envio vem depois da última seção. Não há campo de código, cidade nem finalidade.

**Celular (até 767 px, abaixo do breakpoint `md`):**
- Margens `px-4 py-5`; seções em `p-4`.
- Todos os campos em uma coluna, exceto Mínimo e Máximo, que ficam lado a lado.
- Personas empilhadas, com o ícone à esquerda do texto. Botões com largura total.
- Campos com 44 px de altura, no mínimo, e fonte de 16 px, para o iPhone não aplicar zoom ao focar.

**Notebook (a partir de `md`):**
- Margens `py-10`; seções em `p-6`.
- Personas em três colunas, com o ícone acima do texto.
- Botões à direita, com largura automática.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `CollectionPage` | `src/features/collection/collection-page.tsx` | nenhuma | nenhum |
| `Welcome` | `src/features/collection/welcome.tsx` | `onStart: () => void` | `Card`, `Button` |
| `CollectionForm` | `src/features/collection/collection-form.tsx` | `segment: Segment`, `personas: PersonaOut[]`, `onCreated: (sessionId: string) => void` | `Form`, `Label`, `Checkbox`, `RadioGroup`, `Button`, `Sonner` |
| `PriceRangeField` | `src/features/collection/price-range-field.tsx` | `floor: number`, `ceiling: number`, `disabled: boolean` | `Slider`, `Input`, `Label` |
| `PersonaOption` | `src/features/collection/persona-option.tsx` | `persona: PersonaOut`, `selected: boolean` | `RadioGroup` |
| `CollectionSkeleton` | `src/features/collection/collection-skeleton.tsx` | nenhuma | `Skeleton` |
| `CollectionMessage` | `src/features/collection/collection-message.tsx` | `tone: "empty" \| "error"`, `title: string`, `description: string`, `onRetry?: () => void` | `Button` |
| `ThankYou` | `src/features/collection/thank-you.tsx` | `total: number` | `Card` |
| `collectionFormSchema` | `src/features/collection/schema.ts` | `(segment: Segment) => ZodSchema` | nenhum |

`Segment` é o tipo gerado de um item de `MetaOptions.segments`. `schema.ts` também exporta `COLLECTION_CITY = "Goiânia"` e `COLLECTION_PURPOSE = "sale"`.

O `collectionFormSchema` junta `consent` de `collectionSchema` (seção 7), `priceMin` e `priceMax` com as regras de `step1Schema` e `personaSlug` de `step2Schema`. As mensagens vêm de `copy.collection.validation`: `consent`, `priceOrder`, `priceEmpty`, `priceRequired` e `persona`.

Ícones de `lucide-react`: `MousePointerClick`, `ChartLine`, `ShieldCheck`, `MapPin`, `Check`, `CircleAlert`, `ArrowRight`, `LoaderCircle`, `TriangleAlert`, `RefreshCw`, `PackageOpen`. Nas personas, por `slug`: `familia` → `Users`, `investidor` → `TrendingUp`, `estudante` → `GraduationCap`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `MetaOptions.segments[]` | O item com `COLLECTION_CITY` e `COLLECTION_PURPOSE` | — |
| `price_floor`, `price_ceiling` | Limites do slider e `copy.collection.price.limits` | `formatBRL` |
| `PersonaOut.slug`, `name`, `description` | Cartões de persona | Texto da API |
| `consent` (`POST /sessions`) | Caixa de consentimento | `true` |
| `price_min`, `price_max`, `persona_slug` | Campos do formulário | Números sem formatação no envio |
| `mode`, `city`, `purpose` | Fixos, não aparecem | `"collection"`, `COLLECTION_CITY`, `COLLECTION_PURPOSE` |
| `SessionOut.id` | Guardado com `setSession(id, "collection")` | — |
| `SessionOut.target_pairs` | Agradecimento | `copy.collection.thanks.body(total)` |

O `participant_code` é gerado pelo servidor e não aparece em nenhuma tela. Nos mockups, as descrições das personas e os limites de preço são exemplos: os valores reais vêm da API, depois da A02 e da E06.

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Tela inicial | Sem sessão guardada | `collection.welcome.*` |
| Carregando | Depois de "Quero participar", com `GET /meta/options` ou `/meta/personas` em andamento | `collection.form.*`, `CollectionSkeleton`; `collection.loadingForm` só para leitores de tela |
| Normal | Metadados carregados | Formulário, com `collection.segment` e `collection.price.limits`; o preço começa nos limites do segmento |
| Erros de validação | Envio com campos inválidos | Mensagens de `collection.validation.*` abaixo de cada campo; foco no primeiro com erro |
| Enviando | `POST /sessions` em andamento | Tudo desabilitado; botão com `collection.submitting` |
| Erro ao enviar | Falha no `POST /sessions` | Aviso com `collection.submitError`; o formulário mantém os valores |
| Vazio | Metadados sem o segmento da coleta ou sem personas | `collection.empty.title`, `collection.empty.description` |
| Erro ao carregar | Falha em `/meta/options` ou `/meta/personas` | `collection.loadError.title`, `collection.loadError.description`, botão `common.retry` |
| Pares | Sessão de coleta com `status = "comparing"` | Componente `ComparePanel` de M4 |
| Agradecimento | `onDone` de M4, ou sessão com `status = "done"` | `collection.thanks.*` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir `/coleta` sem sessão | Mostra a tela inicial, sem chamar a API | — |
| Abrir `/coleta` com sessão de modo `collection` guardada | `comparing` retoma os pares; `done` mostra o agradecimento; `404` limpa a sessão e mostra a tela inicial | `GET /sessions/{id}`; `['session', id]` |
| Abrir `/coleta` com sessão de outro modo | Ignora a sessão guardada e mostra a tela inicial | — |
| Botão "Quero participar" | Mostra o formulário e carrega os metadados | `['meta', 'options']`, `['meta', 'personas']` |
| Mover o slider ou editar Mínimo e Máximo | Os dois ficam sincronizados, em passos de R$ 10.000 | — |
| Enviar formulário válido | Cria a sessão e passa aos pares | `POST /sessions` |
| Terminar os pares | Mostra o agradecimento | `['session', id]` |
| Botão "Tentar de novo" | Refaz as consultas dos metadados | `['meta', 'options']`, `['meta', 'personas']` |

O agradecimento não tem botão nem link: a recompensa com feed foi cortada (seção 1.7).

## Textos (chaves de copy.ts usadas nesta tela)
`common.appName`, `common.demoCatalog`, `common.retry`; `collection.*`; e as chaves de M4 listadas em `m4-comparar.md`.

## Critérios de aceite visual (lista verificável)
- [ ] A tela inicial explica o experimento, o que a pessoa fará e o uso das respostas, e diz que nenhum dado pessoal é coletado, antes de qualquer campo.
- [ ] Em nenhuma tela há campo de código, nome, e-mail, telefone, cidade ou finalidade.
- [ ] Em 375 px, não há rolagem horizontal em nenhum estado, e todos os campos têm 44 px de altura ou mais.
- [ ] Em 1280 px, a coluna tem no máximo `max-w-2xl`, e as personas ficam em três colunas.
- [ ] "Imóveis à venda em Goiânia-GO" aparece acima da faixa de preço.
- [ ] Cada erro aparece junto do campo, com ícone e texto, sem depender só da cor.
- [ ] A persona selecionada tem fundo, borda e marca visíveis.
- [ ] Depois de enviar, recarregar a página volta ao par pendente; depois do último par, volta ao agradecimento.
- [ ] O selo "Catálogo de demonstração" aparece no cabeçalho em todas as etapas.
- [ ] As cores vêm só das variáveis de `theme.css`, e nenhum texto visível está escrito direto no componente.
