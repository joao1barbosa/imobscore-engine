# M3b · Modo demo
Rota: /demo   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Com um toque em um perfil, criar a sessão de demonstração e levar o visitante às 3 comparações.

## Layout (celular e notebook)

**Comum:** `PageHeader` sem `active`, título, frase de apoio e três cartões. O cartão inteiro é o botão.

**Celular:** cartões empilhados, com ícone à esquerda; os três cabem sem rolagem em 375 × 667 px.

**Notebook:** bloco centralizado em `max-w-4xl`; cartões em três colunas, com ícone acima do texto.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `DemoPage` | `src/features/demo/demo-page.tsx` | nenhuma | `Skeleton`, `Sonner` |
| `DemoPersonaCard` | `src/features/demo/demo-persona-card.tsx` | `persona: PersonaOut`, `state: "idle" \| "active" \| "dimmed"`, `disabled: boolean`, `onChoose: () => void` | Nenhum: é um `<button>` com as classes do mockup |
| `DemoMessage` | `src/features/demo/demo-message.tsx` | `tone: "empty" \| "error"`, `onRetry?: () => void` | `Button` |

Ícones de `lucide-react`: `LoaderCircle`, `TriangleAlert`, `RefreshCw`, `PackageOpen`. Nas personas, por `slug`: `familia` → `Users`, `investidor` → `TrendingUp`, `estudante` → `GraduationCap`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| `PersonaOut.slug`, `name`, `description` | Cartão | Texto da API |
| `demo_defaults.price_min`, `price_max` | Linha da faixa no cartão | `copy.demo.range(formatBRL(min), formatBRL(max))` |
| `demo_defaults.city`, `purpose` | Não aparecem; vão no `POST /sessions` | — |
| `SessionOut.id` | `setSession(id, "demo")` | — |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Carregando | `GET /meta/personas` em andamento | `demo.title`, `demo.lead`, três `Skeleton`; `demo.loading` só para leitores de tela |
| Normal | Personas carregadas | `demo.title`, `demo.lead`, cartões |
| Enviando | `POST /sessions` em andamento | Cartão tocado com anel e `LoaderCircle`; os outros com `opacity-50`; todos desabilitados; `demo.submitting` |
| Erro ao enviar | Falha no `POST /sessions` | Aviso com `onboarding.submitError`; cartões habilitados de novo |
| Vazio | Sem personas | `onboarding.empty.*` |
| Erro ao carregar | Falha em `/meta/personas` | `onboarding.loadError.*`, botão `common.retry` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Abrir a tela | Carrega as personas | `['meta', 'personas']` |
| Tocar em um cartão | Cria a sessão com `mode = "demo"` e os `demo_defaults` da persona, e vai para `/comparar` | `POST /sessions` |
| Toque durante o envio | Ignorado | — |
| Botão "Tentar de novo" | Refaz a consulta | `['meta', 'personas']` |

## Textos (chaves de copy.ts usadas nesta tela)
`common.appName`, `common.demoCatalog`, `common.retry`; `demo.*`; `onboarding.submitError`, `onboarding.empty.*`, `onboarding.loadError.*`.

## Critérios de aceite visual (lista verificável)
- [ ] Os três cartões cabem sem rolagem em 375 × 667 px.
- [ ] Um único toque, sem formulário, leva a `/comparar`.
- [ ] O cartão inteiro é um único `<button>`, com `aria-label` de `demo.chooseLabel` e foco visível.
- [ ] Cada cartão mostra a faixa de preço que será usada.
- [ ] Um segundo toque durante o envio não gera outro `POST`.
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
