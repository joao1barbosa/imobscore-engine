# M3 · Onboarding
Rota: /comecar   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Coletar a faixa de preço e o perfil em dois passos curtos e criar a sessão de 8 comparações.

## Layout (celular e notebook)

**Comum:** `PageHeader` sem `active`, indicador de passo, título, frase de apoio, conteúdo do passo e botões. Não há campo de cidade nem de finalidade: o aviso "Imóveis à venda em Goiânia-GO" é fixo.

**Celular:** coluna única; Mínimo e Máximo lado a lado; personas empilhadas, com ícone à esquerda; botões com largura total, com o principal acima de "Voltar".

**Notebook:** passo 1 em `max-w-2xl`; passo 2 em `max-w-4xl`, com personas em três colunas e ícone acima do texto; "Voltar" à esquerda e o botão principal à direita.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `OnboardingPage` | `src/features/onboarding/onboarding-page.tsx` | nenhuma | `Form`, `Progress`, `Button`, `Sonner` |
| `StepPrice` | `src/features/onboarding/step-price.tsx` | `segment: Segment`, `disabled: boolean` | `Card` |
| `StepPersona` | `src/features/onboarding/step-persona.tsx` | `personas: PersonaOut[]`, `disabled: boolean` | `RadioGroup` |
| `OnboardingSkeleton` | `src/features/onboarding/onboarding-skeleton.tsx` | nenhuma | `Skeleton` |
| `OnboardingMessage` | `src/features/onboarding/onboarding-message.tsx` | `tone: "empty" \| "error"`, `title: string`, `description: string`, `onRetry?: () => void` | `Button` |

Reaproveite `PriceRangeField` e `PersonaOption` de `src/features/collection/`, sem editá-los. Os schemas são `step1Schema` e `step2Schema` da seção 7, em `src/features/onboarding/schema.ts`, com mensagens de `copy.collection.validation`.

Ícones de `lucide-react`: `MapPin`, `ArrowLeft`, `ArrowRight`, `Check`, `CircleAlert`, `LoaderCircle`, `TriangleAlert`, `RefreshCw`, `PackageOpen`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `MetaOptions.segments[]` | O item com `COLLECTION_CITY` e `COLLECTION_PURPOSE` (de `collection/schema.ts`) | — |
| `price_floor`, `price_ceiling` | Limites do slider e `copy.collection.price.limits` | `formatBRL` |
| `PersonaOut.slug`, `name`, `description` | Cartões de persona | Texto da API |
| `price_min`, `price_max`, `persona_slug` (`POST /sessions`) | Campos do formulário | Números sem formatação no envio |
| `mode`, `city`, `purpose` | Fixos, não aparecem | `"product"`, `COLLECTION_CITY`, `COLLECTION_PURPOSE` |
| `SessionOut.id` | `setSession(id, "product")` | — |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Carregando | `GET /meta/options` ou `/meta/personas` em andamento | `onboarding.price.*`, `OnboardingSkeleton`; `onboarding.loading` só para leitores de tela |
| Passo 1 | Metadados carregados | `onboarding.step(1, 2)`, `onboarding.price.*`, `collection.segment`, `collection.price.*`, `onboarding.next` |
| Passo 2 | Faixa válida | `onboarding.step(2, 2)`, `onboarding.persona.*`, `onboarding.back`, `onboarding.submit` |
| Erro de validação | "Continuar" ou envio com dado inválido | `collection.validation.*`, junto do campo |
| Enviando | `POST /sessions` em andamento | Tudo desabilitado; botão com `onboarding.submitting` |
| Erro ao enviar | Falha no `POST /sessions` | Aviso com `onboarding.submitError`; mantém os valores |
| Vazio | Sem o segmento ou sem personas | `onboarding.empty.*` |
| Erro ao carregar | Falha nos metadados | `onboarding.loadError.*`, botão `common.retry` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Carrega os metadados | `['meta', 'options']`, `['meta', 'personas']` |
| Mover o slider ou editar os campos | Sincroniza os dois, em passos de R$ 10.000 | — |
| Botão "Continuar" | Valida a faixa e vai ao passo 2, sem mudar de rota | — |
| Botão "Voltar" | Volta ao passo 1, mantendo os valores | — |
| Botão "Começar as comparações" | Cria a sessão e vai para `/comparar` | `POST /sessions` |
| Botão "Tentar de novo" | Refaz as consultas | `['meta', 'options']`, `['meta', 'personas']` |

## Textos (chaves de copy.ts usadas nesta tela)
`common.appName`, `common.demoCatalog`, `common.retry`; `onboarding.*`; `collection.segment`, `collection.price.*`, `collection.validation.*`.

## Critérios de aceite visual (lista verificável)
- [ ] O indicador mostra "Passo 1 de 2" e "Passo 2 de 2", com a barra em `aria-live="polite"`.
- [ ] Não há campo de cidade nem de finalidade, e "Imóveis à venda em Goiânia-GO" aparece no passo 1.
- [ ] Em 375 px, não há rolagem horizontal, e os campos têm 44 px de altura ou mais.
- [ ] Em 1280 px, as personas ficam em três colunas.
- [ ] O perfil selecionado tem fundo, borda e marca visíveis.
- [ ] Cada erro aparece junto do campo, com ícone e texto.
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
