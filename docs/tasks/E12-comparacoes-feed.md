# E12 · Comparações da demo e feed com Antes e Depois

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sáb 07/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Completar as comparações da demo e implementar o feed com a alternância Antes e Depois.

## Arquivos permitidos

`src/features/compare/*` (só para aceitar os modos demo e produto); `src/features/feed/*`, com os componentes de `m5-feed.md`; seus testes; `src/api/queries.ts`; `src/mocks/handlers.ts`; `src/app/router.tsx`.

## Dependências

E10, E11

## Especificação

- **Comparações:** reaproveitar o componente de M4. Pré-carregar o próximo par com `queryClient.prefetchQuery` assim que a resposta for aceita. Ao terminar, ir para `/feed`. Depois de cada resposta, invalidar `['session', id]`, `['feed', id]` e `['posterior', id]`.
- **Feed:** seção 7 ("Feed"). Chaves de query `['feed', id, method, at]`. \[C2\] Os motivos aparecem como chips; com o corte C2, o cartão mostra só score e intervalo.
- **Testes:** a alternância Antes e Depois troca a ordem renderizada; o selo mostra o número e a faixa de cor certa nos limites 39, 40, 69 e 70; os estados vazio e de erro mostram os textos de `copy.ts`.

## Verificação

`pnpm test:run && pnpm lint && pnpm typecheck`; com `make dev`, o fluxo da demo completo funciona.

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
| `/comecar` | Onboarding | M3 | Passo 1: cidade, finalidade, faixa de preço. Passo 2: cartões das 3 personas | E11 |
| `/demo` | Modo demo | M3b | 3 cartões de persona; um toque cria a sessão `demo` com `demo_defaults` e vai para `/comparar` | E11 |
| `/comparar` | Comparações | M4 | Dois cartões lado a lado (empilhados no celular), barra de progresso, atalhos ← e → | E12 |
| `/feed` | Feed | M5 | Lista de até 30 imóveis com selo de score, intervalo e até 4 motivos \[C2\]; alternância Antes e Depois | E12 |
| `/modelo` | Painel do modelo | M6 | Pesos da priori e da posteriori com intervalos; traço das cadeias \[C4\]; diagnósticos | E13 |
| `/experimento` | Painel do experimento | M7 | Acurácia por número de pares (uma linha por método) e por participante | E14 |
| `/imovel/:id` | Detalhe e vistoria | M8 | Só se o corte C1 for revertido | E17 |

### Seção 7 · Comparações e feed

**Comparações (`features/compare`).** Busca `GET /next-pair`. O cartão escolhido sai com animação do Framer Motion (`AnimatePresence`), e o tempo de resposta é medido com `performance.now()` desde que o par aparece. As teclas ← e → escolhem; botões são desabilitados enquanto a resposta é enviada, para evitar duplo clique. Ao receber `done: true`, navega para `/feed` (ou para a tela de agradecimento, no modo coleta). O próximo par é pré-carregado com `queryClient.prefetchQuery` assim que a resposta é aceita.

**Feed (`features/feed`).** Uma única consulta `useQuery` a `GET /sessions/{id}/feed?limit=30`, sem rolagem infinita. Cada cartão mostra o selo com o score (ex.: "87"), com o texto "87% de chance de você preferir este a um imóvel típico" no tooltip, o intervalo ("entre 71 e 95") e os motivos como chips \[C2\]. A alternância **Antes e Depois** faz duas consultas: `at=0` (só a priori) e `at=<n respondidos>`. Os itens usam `motion.li` com `layout` e `key = listing.id`, então a troca anima a reordenação sozinha. Esse é o "momento uau" da demo. Sem link para o detalhe enquanto o corte C1 valer.

### Seção 5.6 · Selo e intervalo

- O intervalo exibido é formado pelos percentis 5 e 95 de a\_s(x), multiplicados por 100.
- O selo diz: "{score}% de chance de você preferir este a um imóvel típico".

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
- Valores com `Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 })`. Aluguel sempre com "/mês".
- Contraste AA, foco visível, `aria-live="polite"` na barra de progresso e textos alternativos nas ilustrações.
- Estados de carregamento com `Skeleton`, e erros com aviso e botão "Tentar de novo". Um `ErrorBoundary` na raiz mostra uma tela de erro amigável.

### Seção 6 · API

Todas as rotas ficam sob `/api/v1`, devolvem JSON em `snake_case` e têm `response_model` declarado, para que o OpenAPI gere os tipos do front-end. A sessão anônima é identificada pelo UUID no caminho.

| Método e rota | Faz | Resposta |
| --- | --- | --- |
| `GET /health` | Verifica a API e o banco (`SELECT 1`) | `{status, db}` |
| `GET /meta/options` | Cidades, finalidades e faixa de preço mínima e máxima por segmento | `MetaOptions` |
| `GET /meta/personas` | As 3 personas, com nome, descrição e `demo_defaults` | `list[PersonaOut]` |
| `GET /meta/features` | As 12 características, com chave, rótulo e textos | `list[FeatureOut]` |
| `GET /meta/inspection-items` | Itens da vistoria com Δ sugerido | `list[InspectionItemOut]` |
| `POST /sessions` | Cria a sessão a partir do onboarding | `201 SessionOut` |
| `GET /sessions/{id}` | Estado da sessão e progresso | `SessionOut` |
| `GET /sessions/{id}/next-pair` | Devolve o par pendente ou cria o próximo. Retorna `204` quando `target_pairs` foi atingido | `PairOut` |
| `POST /sessions/{id}/comparisons/{position}` | Registra a escolha. Fora do modo coleta, recalcula a posteriori | `AnswerOut` |
| `GET /sessions/{id}/feed` | Feed paginado, com `method=bayes` (padrão) ou `method=persona` | `FeedPage` |
| `GET /sessions/{id}/posterior` | Pesos (priori e posteriori), intervalos e diagnósticos | `PosteriorOut` |
| `GET /sessions/{id}/posterior/trace?feature=log_price` | Traço das 4 primeiras cadeias de um peso, com os 250 pontos guardados de cada uma (corte C4) | `TraceOut` |
| `GET /listings/{id}?session_id=` | Detalhe do imóvel, com score, explicação e vistoria da sessão | `ListingDetailOut` |
| `PUT /sessions/{id}/inspections/{listing_id}` | Substitui os ajustes da vistoria desse imóvel | `ListingDetailOut` |
| `GET /experiment/summary?run_id=` | Métricas agregadas da última rodada (ou da `run_id` pedida) | `ExperimentSummary` |

**No prazo curto:** `GET /listings/{id}` e `PUT /sessions/{id}/inspections/{listing_id}` só são implementadas se João reverter o corte C1 (tarefa E17). Sem C1, o feed devolve `inspection_delta = 0`.

#### Schemas principais (Pydantic)

```python
class SessionCreate(BaseModel):
    mode: Literal["product", "demo", "collection"] = "product"
    city: str
    purpose: Literal["sale", "rent"]
    price_min: Decimal = Field(gt=0)
    price_max: Decimal = Field(gt=0)
    persona_slug: Literal["familia", "investidor", "estudante"]
    consent: bool = False
    # model_validator: price_min < price_max; collection exige consent=True, city="Goiânia" e purpose="sale"; o servidor gera participant_code

class SessionOut(BaseModel):
    id: UUID; mode: str; city: str; purpose: str
    price_min: Decimal; price_max: Decimal; persona_slug: str
    target_pairs: int; answered: int; status: Literal["comparing", "done"]

class ListingCard(BaseModel):
    id: UUID; code: str; title: str; neighborhood: str; city: str
    purpose: str; kind: str; price_brl: Decimal; area_m2: float
    bedrooms: int; bathrooms: int; parking: int; dist_center_km: float
    age_years: int; leisure_count: int; pet_friendly: bool; doorman_24h: bool
    illustration: str

class PairOut(BaseModel):
    position: int; total: int
    listing_a: ListingCard; listing_b: ListingCard

class AnswerIn(BaseModel):
    chosen: Literal["A", "B"]
    response_ms: int = Field(ge=0, le=600_000)

class AnswerOut(BaseModel):
    answered: int; total: int; done: bool
    diagnostics: "Diagnostics | None"   # None no modo coleta

class Reason(BaseModel):
    feature_key: str; text: str; contribution: float

class FeedItem(BaseModel):
    listing: ListingCard
    score: int                      # 0..100, já com a vistoria
    affinity_pct: float             # 100 x afinidade, sem a vistoria
    interval: tuple[float, float]   # percentis 5 e 95, em %
    inspection_delta: int
    reasons: list[Reason]           # vazia quando method=persona
    rank: int

class FeedPage(BaseModel):
    items: list[FeedItem]; next_offset: int | None
    method: Literal["bayes", "persona"]; n_comparisons: int

class Diagnostics(BaseModel):
    accept_rate: float; rhat_max: float; ess_min: float
    step_size: float; elapsed_ms: int; ok: bool

class WeightOut(BaseModel):
    feature_key: str; label: str
    prior_mean: float; prior_sd: float
    post_mean: float; post_sd: float; ci_low: float; ci_high: float

class PosteriorOut(BaseModel):
    n_comparisons: int; weights: list[WeightOut]; diagnostics: Diagnostics
```

#### Regras da API

- **Idempotência:** `POST /comparisons/{position}` em uma posição já respondida devolve `409 pair_already_answered`. Uma posição diferente da pendente devolve `409 pair_out_of_order`.
- **Retomada:** `GET /next-pair` devolve o par pendente (`chosen IS NULL`), se houver, em vez de criar outro. Recarregar a página não pula pares.
- **Fim:** quando `answered == target_pairs`, `GET /next-pair` devolve `204` sem corpo, e `status` da sessão passa a `done`. `POST` numa sessão `done` devolve `409 session_done`.
- **Candidatos:** pares e feed usam o mesmo conjunto, calculado por uma única função `candidate_listings(session)`: imóveis da cidade e da finalidade da sessão com preço entre 0,85 × `price_min` e 1,15 × `price_max`; se forem menos de 20, todos os imóveis da cidade e da finalidade. A lista é sempre ordenada por `code`.
- **Feed:** com 0 pares respondidos, usa amostras da priori. O parâmetro opcional `at=N` devolve o feed calculado com os N primeiros pares (`at=0` é só a priori), usado na alternância Antes e Depois. `limit` vai de 1 a 50, com padrão 30. `offset` existe e tem padrão 0, mas o front-end usa só a primeira página. Ordem: afinidade média decrescente; empate pelo `code`.
- **Cache:** o ranking é guardado em memória por `(session_id, n_comparisons, method)`, até 128 entradas.
- **Erros:** formato único `{"detail": {"code": "...", "message": "..."}}`, com mensagem em pt-BR. Códigos: `session_not_found` (404), `listing_not_found` (404), `pair_already_answered` (409), `pair_out_of_order` (409), `session_done` (409), `validation_error` (422), `not_available` (501). Um handler global converte o `RequestValidationError` do FastAPI para esse formato.
- **CORS:** liberado só para `http://localhost:5173` (desenvolvimento). Com o Docker Compose, o Nginx serve front-end e API na mesma origem.
- **Configuração (`.env`):** `DATABASE_URL`, `MCMC_CHAINS=16`, `MCMC_WARMUP=1000`, `MCMC_DRAWS=2000`, `MCMC_THIN=8`, `PRIOR_SD=1.0`, `PAIRS_DEMO=3`, `PAIRS_PRODUCT=8`, `PAIRS_COLLECTION=25`, `CATALOG_SEED=42`, `LOG_LEVEL=INFO`, `CORS_ORIGINS=http://localhost:5173`.
