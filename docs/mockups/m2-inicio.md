# M2 · Início
Rota: /   Versão: 1   Status: ver APPROVAL.md

## Objetivo (1 frase)
Dizer em uma frase o que o ImobScore faz e levar a pessoa para o fluxo completo ou para a demo.

## Layout (celular e notebook)

**Comum:** `PageHeader` sem `active`, depois a frase principal, o texto de apoio, os dois botões, três cartões numerados e uma linha final com o aviso do catálogo e o link do experimento.

**Celular:** tudo à esquerda; botões empilhados, com largura total; cartões empilhados, com ícone à esquerda.

**Notebook:** bloco principal centralizado, com `text-6xl` na frase; botões lado a lado; cartões em três colunas, com ícone acima do texto.

## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
| --- | --- | --- | --- |
| `HomePage` | `src/features/home/home-page.tsx` | nenhuma | `Button` |
| `HomeStep` | `src/features/home/home-step.tsx` | `index: number`, `icon: LucideIcon`, `title: string`, `body: string` | `Card` |

Ícones de `lucide-react`: `ArrowRight`, `Zap`, `UserRound`, `MousePointerClick`, `ListOrdered`.

## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
| --- | --- | --- |
| Nenhum | A tela não chama a API | — |

## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
| --- | --- | --- |
| Normal | Sempre | `home.*` |

## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
| --- | --- | --- |
| Botão "Começar" | Vai para `/comecar` | — |
| Botão "Modo demo" | Vai para `/demo` | — |
| Link dos resultados | Vai para `/experimento` | — |

## Textos (chaves de copy.ts usadas nesta tela)
`common.appName`, `common.demoCatalog`; `home.*`.

## Critérios de aceite visual (lista verificável)
- [ ] "Pare de filtrar. Comece a escolher." é o maior texto da tela e aparece sem rolagem em 375 × 667 px.
- [ ] Os dois botões aparecem sem rolagem em 375 × 667 px, com "Começar" em destaque.
- [ ] Em 1280 px, os três cartões ficam lado a lado.
- [ ] A tela diz que os imóveis são fictícios e mostra o selo "Catálogo de demonstração".
- [ ] As cores vêm só de `theme.css`, e nenhum texto visível está escrito direto no componente.
