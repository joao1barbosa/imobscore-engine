# E14 · Painel do experimento

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sáb 07/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

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

## Regras gerais

- Todo código numérico recebe um `numpy.random.Generator` com semente explícita. Nada usa o estado global de `np.random`.
- Textos da interface em português do Brasil. Nomes de código, tabelas e colunas em inglês.
- Os dados do catálogo são simulados, e a interface diz isso ("catálogo de demonstração").
- Nada depende de internet em execução: sem CDN, sem fontes remotas e sem imagens externas. A única exceção são os mockups em `docs/mockups/`, que não fazem parte do app.
- Claude, ao encontrar uma decisão não prevista, escolhe a opção mais simples compatível com o plano e registra uma linha em `docs/decisions.md`. O executor não decide: pergunta (1.5).
- Ao fim de cada tarefa, o dono atualiza `docs/STATUS.md`.

**Dependências que travam o trabalho.** E05 espera A01 (precisa de `theme.css`). E06 espera A02. E07 espera A03 (`seed_for` e `random_pairs`). E08 espera M1 e M4 aprovados. E10 espera A06 marcada como concluída em `docs/STATUS.md`. E11 a E14 esperam G2. Se uma dependência atrasar, o executor passa para a próxima tarefa sem dependência pendente e registra o atraso em `docs/STATUS.md`.

- Apagar o `.gitkeep` de uma pasta que passou a ter outros arquivos faz parte da tarefa, mesmo sem constar em "Arquivos permitidos".

## Contexto do plano

Trechos copiados de `docs/PLAN.md`. Menções a "seção N" se referem ao plano, e o necessário para esta tarefa está aqui. Se um trecho conflitar com as partes acima deste título, valem as de cima.

### Seção 1.6 · Mockups e aprovação das telas

Nenhuma tela é implementada antes de João aprovar o mockup dela. O mockup é a fonte da verdade visual: onde a seção 7 e o mockup aprovado divergirem, vale o mockup.

**Formato de cada mockup** (feito por Claude):

- `docs/mockups/<id>-<nome>.html`: HTML estático que abre direto no navegador. Usa Tailwind por CDN (só nos mockups, nunca no app), as mesmas variáveis de cor e fonte de `theme.css` e dados realistas do catálogo simulado. Mostra a tela em celular (375 px) e notebook (1280 px), lado a lado, e todos os estados: normal, carregando, vazio e erro.
- `docs/mockups/<id>-<nome>.md`: a especificação que o executor segue, com estas partes, nesta ordem:

```markdown
# <ID> · <Nome da tela>
Rota: /...   Versão: 1   Status: ver APPROVAL.md
## Objetivo (1 frase)
## Layout (celular e notebook)
## Componentes
| Componente | Arquivo a criar | Props (nome: tipo) | Componentes shadcn usados |
## Dados
| Campo da API (seção 6) | Onde aparece | Formato (função de lib/format.ts) |
## Estados
| Estado | Quando ocorre | O que mostra (chave de copy.ts) |
## Interações
| Ação do usuário | Resultado | Endpoint ou query key |
## Textos (chaves de copy.ts usadas nesta tela)
## Critérios de aceite visual (lista verificável)
```

**Fluxo de aprovação**

1. Claude abre os HTML no navegador de João e explica, em até 5 frases por tela, as decisões de UX: o que o visitante vê primeiro, o que precisa caber em 60 segundos de demo e como a tela funciona no celular.
2. João responde "aprovado", pede ajustes ou rejeita. Claude ajusta até a aprovação.
3. Claude registra em `docs/mockups/APPROVAL.md` uma linha por tela: `| ID | versão | aprovado | data | observações de João |`.
4. Só a palavra "aprovado" nesse arquivo libera a tarefa E da tela. Mudanças depois disso exigem pedido de João e uma nova versão.

| ID | Tela | Rota | Gate | Prazo de aprovação |
| --- | --- | --- | --- | --- |
| M1 | Coleta: tela inicial, consentimento, faixa de preço, persona e agradecimento | `/coleta` | G1 | qua 04/11, 16h |
| M4 | Comparação de um par (usada na coleta e na demo) | `/comparar` | G1 | qua 04/11, 16h |
| M2 | Início | `/` | G2 | qui 05/11, 18h |
| M3 | Onboarding em dois passos | `/comecar` | G2 | qui 05/11, 18h |
| M3b | Modo demo | `/demo` | G2 | qui 05/11, 18h |
| M5 | Feed com Antes e Depois | `/feed` | G2 | qui 05/11, 18h |
| M6 | Painel do modelo | `/modelo` | G2 | qui 05/11, 18h |
| M7 | Painel do experimento | `/experimento` | G2 | qui 05/11, 18h |
| M8 | Detalhe do imóvel e vistoria | `/imovel/:id` | Só com o corte C1 revertido | seg 09/11, 12h |

### Seção 1.7 · Escopo no prazo curto

**Essencial (não corta):** o motor completo (seções 5.1 a 5.9) com testes; a coleta e a avaliação com dados reais, ou simulados e declarados como tal; o fluxo da demo (persona, 3 pares, feed com Antes e Depois); os painéis do modelo e do experimento; e a execução offline.

**Já cortado (não implementar):**

| Item | Onde aparecia | O que fica no lugar |
| --- | --- | --- |
| Rolagem infinita do feed | 7 | Uma consulta só, com `limit=30` |
| Aba Lado a lado | 7 | A alternância Antes e Depois |
| Recompensa com feed ao fim da coleta | 7 | Tela de agradecimento |
| GitHub Actions e pre-commit | 2 | `make check` rodado no notebook (seção 9) |
| Playwright | 2, 9 | Roteiro manual offline (seção 9) |
| `dev:mock` no navegador | 2 | MSW só nos testes |
| Cobertura mínima no front-end | 2 | Testes dos fluxos críticos listados em cada tarefa |

**Cortes condicionais**, nesta ordem, decididos por João em 09/11 às 12h:

| Corte | O que sai | O que fica |
| --- | --- | --- |
| C1 · já aplicado, reversível | Detalhe do imóvel e vistoria (M8, tarefa E17) | Cartão do feed sem link |
| C2 | Motivos "por que este imóvel" no cartão | Score e intervalo |
| C3 | Escolha adaptativa de pares (BALD) | Pares aleatórios também na demo |
| C4 | Gráfico de traço das cadeias no painel do modelo | Quadro de diagnósticos |

### Seção 7 · Rotas do front-end

| Rota | Tela | Mockup | Conteúdo | Tarefa |
| --- | --- | --- | --- | --- |
| `/coleta` | Coleta | M1 + M4 | Tela inicial, consentimento, faixa de preço (Goiânia, compra), persona, 25 pares e agradecimento; o servidor gera o código do participante | E08 (primeira a ficar pronta) |
| `/` | Início | M2 | Frase "Pare de filtrar. Comece a escolher.", botão Começar e botão Modo demo | E11 |
| `/comecar` | Onboarding | M3 | Passo 1: faixa de preço (Goiânia, compra). Passo 2: cartões das 3 personas | E11 |
| `/demo` | Modo demo | M3b | 3 cartões de persona; um toque cria a sessão `demo` com `demo_defaults` e vai para `/comparar` | E11 |
| `/comparar` | Comparações | M4 | Dois cartões lado a lado (empilhados no celular), barra de progresso, atalhos ← e → | E12 |
| `/feed` | Feed | M5 | Lista de até 30 imóveis com selo de score, intervalo e até 4 motivos \[C2\]; alternância Antes e Depois | E12 |
| `/modelo` | Painel do modelo | M6 | Pesos da priori e da posteriori com intervalos; traço das cadeias \[C4\]; diagnósticos | E13 |
| `/experimento` | Painel do experimento | M7 | Acurácia por número de pares (uma linha por método) e por participante | E14 |
| `/imovel/:id` | Detalhe e vistoria | M8 | Só se o corte C1 for revertido | E17 |

### Seção 7 · Painel do experimento

**Painel do experimento (`features/experiment`).** Linhas de acurácia contra n\_train (3, 5, 10, 15), uma por método, com faixa de ±1 desvio, e uma tabela com acurácia e perda logarítmica. Se a rodada tiver participantes simulados, um aviso fixo diz "Dados simulados".

### Seção 7 · Dados e estado

- **Cliente:** `openapi-fetch` com o tipo `paths` de `src/api/schema.d.ts` e `baseUrl: "/api/v1"`. No dev, o Vite faz proxy de `/api` para `http://localhost:8000`.
- **Chaves de query:** `['meta', 'options']`, `['meta', 'personas']`, `['session', id]`, `['pair', id]`, `['feed', id, method, at]`, `['posterior', id, n]`, `['trace', id, n, feature]`, `['listing', id, sessionId]`, `['experiment', runId]`. Todas ficam em `src/api/queries.ts` como funções `queryOptions(...)`.
- **Padrões do `QueryClient`:** `retry: 1`, `refetchOnWindowFocus: false`. Dados de `meta` usam `staleTime: Infinity`, porque não mudam durante a sessão.
- **Depois de responder um par:** invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
- **Zustand:** `{ sessionId, mode, setSession, reset }`, com `persist` no `localStorage` dentro de `try/catch`. Sem `sessionId` válido, as rotas protegidas redirecionam para `/comecar`.

### Seção 7 · Visual e acessibilidade

- Componentes do shadcn/ui, sobre Base UI: `Button`, `Card`, `Badge`, `Progress`, `Slider`, `Select`, `RadioGroup`, `Tabs`, `Tooltip`, `Switch`, `Skeleton`, `Sonner` (avisos).
- Fonte Geist instalada via `@fontsource-variable/geist`, para funcionar offline. Nada de Google Fonts.
- Cores como variáveis CSS do tema do shadcn, com modo escuro. O selo de score tem três faixas (0 a 39, 40 a 69, 70 a 100) e sempre mostra o número, para não depender só da cor.
- Valores com `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 })`.
- Contraste AA, foco visível, `aria-live="polite"` na barra de progresso e textos alternativos nas ilustrações.
- Estados de carregamento com `Skeleton`, e erros com aviso e botão "Tentar de novo". Um `ErrorBoundary` na raiz mostra uma tela de erro amigável.

### Tarefa E10 · `GET /experiment/summary`

- **`GET /experiment/summary?run_id=`:** sem `run_id`, usa a rodada mais recente (maior `created_at`). Schemas:

```python
class ExperimentRow(BaseModel):
    method: Literal["equal", "persona", "mle", "bayes"]; n_train: int
    acc_mean: float; acc_sd: float; ll_mean: float; ll_sd: float; n_participants: int
class ParticipantRow(BaseModel):
    participant_code: str; method: str; acc_mean: float      # sempre n_train = 5
class ExperimentSummary(BaseModel):
    run_id: UUID | None; simulated: bool; participants: int
    rows: list[ExperimentRow]; per_participant: list[ParticipantRow]
```

`simulated` é verdadeiro se algum `participant_code` começar com "S". Sem resultados: `run_id = null` e listas vazias.

### Seção 6 · Erros

- **Erros:** formato único `{"detail": {"code": "...", "message": "..."}}`, com mensagem em pt-BR. Códigos: `session_not_found` (404), `listing_not_found` (404), `pair_already_answered` (409), `pair_out_of_order` (409), `session_done` (409), `validation_error` (422), `not_available` (501). Um handler global converte o `RequestValidationError` do FastAPI para esse formato.
