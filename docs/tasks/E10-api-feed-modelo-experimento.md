# E10 · API do feed, do modelo e do experimento

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sex 06/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Implementar as rotas e os serviços de posteriori, feed, modelo e experimento, além do modo adaptativo de pares.

## Arquivos permitidos

`backend/app/services/posterior_service.py`, `feed_service.py`, `experiment_service.py`, `pair_service.py` (acrescentar o modo adaptativo); `backend/app/schemas/feed.py`, `posterior.py`, `experiment.py`; `backend/app/api/v1/__init__.py` (registrar as rotas novas), `feed.py`, `posterior.py`, `experiment.py`, `meta.py` (acrescentar `/meta/features` e `/meta/inspection-items`), `sessions.py` (acrescentar o recálculo depois da resposta); o comando `load-results` em `backend/app/cli.py`; testes em `backend/tests/api/` e `backend/tests/services/`.

## Dependências

A06 concluída em `docs/STATUS.md`

## Especificação

- **`posterior_service.get_or_fit(session, n) -> MCMCResult`:** se existir linha em `posteriors` com `(session_id, n_comparisons = n)`, carrega as amostras (`np.load` do `bytea`, convertido para `float64`) e devolve. Senão: D = z(vencedor) − z(perdedor) dos n primeiros pares respondidos, em ordem de `position`, com z = `standardize(raw_matrix(...), center, scale)` do segmento da sessão; `mu` e `sd` vêm de `personas.prior_mean` e `prior_sd`, na ordem de `FEATURE_KEYS`; `fit_posterior(D, mu, sd, seed_for(session.id, n), MCMCConfig(...))` com os valores de `MCMC_*` das configurações; grava a linha (amostras em `float32` com `np.save`, `mean`, `sd`, `ci_low` e `ci_high` por chave, campos de diagnóstico e `seed`) e devolve.
- **Depois de cada resposta** (`POST /comparisons`), nos modos `demo` e `product`: chamar `get_or_fit(session, answered)` e devolver os diagnósticos em `AnswerOut`. No modo `collection`, não roda MCMC e devolve `diagnostics = null`.
- **`GET /next-pair` nos modos `demo` e `product`:** candidatos de `candidate_listings`; `Z` padronizado; `samples = get_or_fit(session, answered).samples`; `shown` = conjunto de `frozenset({i, j})` dos pares já mostrados, em índices dos candidatos; `next_pair_bald(Z, samples, shown, np.random.default_rng(seed_for(session.id, 10_000 + answered)))`; gravar com `selection = 'adaptive'`. Com o corte C3, usar `random_pairs` como na coleta.
- **`GET /sessions/{id}/feed?method=bayes|persona&at=N&limit=30&offset=0`:** `n = at` se informado, senão `answered`; `at` fora de 0..answered devolve 422. `bayes`: `samples` de `get_or_fit(session, n)`, `compute_affinity(Z, samples)` e `explain(Z[i], samples.mean(0))`. `persona`: `samples = mu[None, :]` e `reasons = []`. Cada `FeedItem`: `score = to_score(mean[i], 0)`, `affinity_pct = round(100 * mean[i], 1)`, `interval = (round(100 * p5[i], 1), round(100 * p95[i], 1))`, `inspection_delta = 0`, `rank` a partir de 1. Ordem e cache conforme a seção 6.
- **`GET /sessions/{id}/posterior?n=`:** um `WeightOut` por chave, com `label` de `FEATURES`, priori da persona e média, desvio e percentis 5 e 95 das amostras; mais os diagnósticos. `n` padrão: `answered`.
- **`GET /sessions/{id}/posterior/trace?feature=<chave>&n=`:** `TraceOut = { feature_key: str, chains: list[list[float]] }`, com `samples.reshape(n_chains, -1, 12)[:4, :, j]`. Chave fora de `FEATURE_KEYS` devolve 422.
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
- **`load-results <csv>`:** insere as linhas em `experiment_results`; se o `run_id` já existir, não faz nada e avisa.
- **Testes:** feed com 0 e com 3 pares; `method=persona`; `at=0` diferente de `at=3`; `at` inválido dá 422; score sempre entre 0 e 100; segunda chamada do feed não roda o MCMC de novo (verificar com `unittest.mock`); posteriori com 12 pesos; traço com 4 cadeias de 250 pontos; resumo vazio e com um CSV de exemplo; demo com 3 pares sem repetir.

## Verificação

`cd backend && uv run pytest -q && uv run ruff check .`.

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

### Seção 4 · Tabelas usadas

```sql
CREATE TABLE listings (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text UNIQUE NOT NULL,              -- ex.: GYN-A-0042
  city            text NOT NULL,                     -- 'Goiânia' | 'Aparecida de Goiânia' | 'Anápolis'
  purpose         text NOT NULL CHECK (purpose IN ('sale','rent')),
  kind            text NOT NULL CHECK (kind IN ('apartment','house')),
  title           text NOT NULL,
  neighborhood    text NOT NULL,
  price_brl       numeric(12,2) NOT NULL CHECK (price_brl > 0), -- venda: preço; aluguel: aluguel + condomínio
  area_m2         numeric(7,1)  NOT NULL CHECK (area_m2 > 0),
  bedrooms        smallint NOT NULL CHECK (bedrooms BETWEEN 1 AND 6),
  bathrooms       smallint NOT NULL CHECK (bathrooms BETWEEN 1 AND 6),
  parking         smallint NOT NULL CHECK (parking BETWEEN 0 AND 4),
  dist_center_km  numeric(5,2) NOT NULL CHECK (dist_center_km >= 0),
  age_years       smallint NOT NULL CHECK (age_years BETWEEN 0 AND 60),
  leisure_count   smallint NOT NULL CHECK (leisure_count BETWEEN 0 AND 3), -- piscina, academia, salão
  pet_friendly    boolean NOT NULL,
  doorman_24h     boolean NOT NULL,
  illustration    text NOT NULL,                     -- chave do SVG local
  created_at      timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_listings_segment ON listings (city, purpose, price_brl);

CREATE TABLE feature_stats (
  city        text NOT NULL,
  purpose     text NOT NULL,
  feature_key text NOT NULL,
  center      double precision NOT NULL,             -- mediana no segmento
  scale       double precision NOT NULL CHECK (scale > 0), -- IQR / 1.349
  PRIMARY KEY (city, purpose, feature_key)
);

CREATE TABLE personas (
  slug            text PRIMARY KEY,                  -- 'familia' | 'investidor' | 'estudante'
  name            text NOT NULL,
  description     text NOT NULL,
  prior_mean      jsonb NOT NULL,                    -- {feature_key: float}, 12 chaves
  prior_sd        jsonb NOT NULL,                    -- {feature_key: float > 0}
  demo_defaults   jsonb NOT NULL                     -- cidade, finalidade e faixa para o modo demo
);

CREATE TABLE sessions (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mode             text NOT NULL CHECK (mode IN ('product','demo','collection')),
  city             text NOT NULL,
  purpose          text NOT NULL CHECK (purpose IN ('sale','rent')),
  price_min        numeric(12,2) NOT NULL,
  price_max        numeric(12,2) NOT NULL,
  persona_slug     text NOT NULL REFERENCES personas(slug),
  target_pairs     smallint NOT NULL,                 -- demo 3, produto 8, coleta 25
  participant_code text,                             -- só na coleta: gerado pelo servidor (P01, P02...)
  consent_at       timestamptz,                      -- obrigatório quando mode = 'collection'
  status           text NOT NULL DEFAULT 'comparing' CHECK (status IN ('comparing','done')),
  created_at       timestamptz NOT NULL DEFAULT now(),
  CHECK (price_min < price_max),
  CHECK (mode <> 'collection' OR (participant_code IS NOT NULL AND consent_at IS NOT NULL))
);

CREATE TABLE comparisons (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id    uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  position      smallint NOT NULL,                   -- 1, 2, 3...
  listing_a_id  uuid NOT NULL REFERENCES listings(id), -- mostrado à esquerda
  listing_b_id  uuid NOT NULL REFERENCES listings(id), -- mostrado à direita
  selection     text NOT NULL CHECK (selection IN ('adaptive','random')),
  chosen        char(1) CHECK (chosen IN ('A','B')),  -- NULL enquanto não respondido
  shown_at      timestamptz NOT NULL DEFAULT now(),
  answered_at   timestamptz,
  response_ms   integer,
  UNIQUE (session_id, position),
  CHECK (listing_a_id <> listing_b_id)
);

CREATE TABLE posteriors (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  session_id     uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  n_comparisons  smallint NOT NULL,
  seed           bigint NOT NULL,
  samples        bytea NOT NULL,                     -- np.save de float32 [4000, 12]
  mean           jsonb NOT NULL,
  sd             jsonb NOT NULL,
  ci_low         jsonb NOT NULL,                     -- percentil 5
  ci_high        jsonb NOT NULL,                     -- percentil 95
  accept_rate    double precision NOT NULL,
  rhat_max       double precision NOT NULL,
  ess_min        double precision NOT NULL,
  step_size      double precision NOT NULL,
  elapsed_ms     integer NOT NULL,
  created_at     timestamptz NOT NULL DEFAULT now(),
  UNIQUE (session_id, n_comparisons)
);

CREATE TABLE experiment_results (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id           uuid NOT NULL,
  participant_code text NOT NULL,
  method           text NOT NULL CHECK (method IN ('equal','persona','mle','bayes')),
  n_train          smallint NOT NULL,                -- 3, 5, 10, 15
  split_seed       integer NOT NULL,
  n_test           smallint NOT NULL,
  accuracy         double precision NOT NULL,
  log_loss         double precision NOT NULL,
  created_at       timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX ix_results_run ON experiment_results (run_id, method, n_train);
```

### Seção 4 · Regras do banco

- As características transformadas e padronizadas não são guardadas. Elas são recalculadas em memória a partir de `listings` e `feature_stats`, porque são baratas e assim a fórmula fica em um só lugar (`engine/features.py`).
- `posteriors.samples` guarda as amostras em `float32` (cerca de 4.000 × 12 × 4 bytes = 192 kB por linha). O feed reaproveita a última posteriori em vez de rodar o MCMC de novo.
- `comparisons.chosen` fica nulo entre mostrar o par e receber a resposta, o que permite retomar a sessão após recarregar a página.
- A convenção de nomes do SQLAlchemy (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) é definida no `MetaData` antes da primeira migração.

### Seção 5.5 · Diagnósticos

- **R-hat dividido:** corte cada cadeia guardada ao meio (32 meias-cadeias de n = 125). Com B = variância entre as médias das meias-cadeias vezes n e W = média das variâncias dentro delas, calcule `rhat = sqrt(((n - 1) / n * W + B / n) / W)` para cada peso.
- **ESS:** autocorrelação média entre as cadeias, somada até a primeira soma de pares consecutivos negativa (Geyer). `ess = S / (1 + 2 * soma)`.
- **Critério:** `rhat_max < 1.05`, `ess_min > 400` e aceitação entre 0,15 e 0,50. Se falhar, rode de novo uma vez com aquecimento e amostras dobrados. Se falhar de novo, grave assim mesmo, registre um aviso no log e devolva `diagnostics.ok = false` na API. Isso não bloqueia o fluxo.

### Seção 5.6 · Afinidade, score e explicação

Com as S = 4.000 amostras guardadas w\_s achatadas em (S, 12) e Z com forma (n, 12):

```latex
a_s(x) = \sigma\left(w_s^\top z(x)\right), \qquad \text{afinidade}(x) = \frac{1}{S}\sum_{s=1}^{S} a_s(x), \qquad \text{score}(x) = \operatorname{clip}\left(\operatorname{round}(100 \cdot \text{afinidade}(x)) + \sum \Delta_{\text{vistoria}},\; 0,\; 100\right)
```

- O intervalo exibido é formado pelos percentis 5 e 95 de a\_s(x), multiplicados por 100.
- O selo diz: "{score}% de chance de você preferir este a um imóvel típico".
- **Explicação:** a contribuição de cada característica é c\_j = w̄\_j · z\_j(x), em que w̄ é a média das amostras. Mostre as 3 maiores contribuições positivas e a mais negativa, usando `text_high` se z\_j > 0 e `text_low` se z\_j < 0. Ignore |c\_j| < 0,1.
- Calcule tudo em lote: `sigmoid(Z @ samples.T)` tem forma (n, S). Para 300 imóveis e 4.000 amostras, isso cabe folgado na memória.

### Seção 5.7 · Escolha do próximo par

- **Candidatos:** imóveis do segmento da sessão com preço entre 0,85 × `price_min` e 1,15 × `price_max`. Se forem menos de 20, use o segmento inteiro.
- **Modo `collection` (coleta):** pares sorteados ao acaso (`selection = 'random'`), sem repetir par e com cada imóvel aparecendo no máximo 3 vezes. A coleta não roda MCMC entre os pares. Os pares precisam ser aleatórios para que a avaliação não dependa de nenhum dos modelos comparados.
- **Modos `product` e `demo`:** escolha adaptativa (`selection = 'adaptive'`). Sorteie K = 300 pares candidatos ainda não mostrados e escolha o de maior informação esperada (BALD). Antes do primeiro par, use 4.000 amostras sorteadas direto da priori.

```latex
p_s = \sigma\left(w_s^\top (z_A - z_B)\right), \quad \bar p = \frac{1}{S}\sum_s p_s, \quad H(p) = -p\log p - (1-p)\log(1-p), \quad \text{BALD} = H(\bar p) - \frac{1}{S}\sum_s H(p_s)
```

- Sorteie qual imóvel vai à esquerda, para não haver viés de posição. O da esquerda é sempre `listing_a`.
- No modo demo, o MCMC roda depois de cada resposta, porque o próximo par depende da posteriori atual.

### Seção 5.10 · Interface pública do motor

O executor só enxerga o motor por estes nomes. Claude implementa todos eles e não muda nenhuma assinatura sem atualizar esta seção e avisar João na mesma alteração. Todos os arrays são `np.ndarray` de `float64`, e "12" é sempre o número de características, na ordem de `FEATURE_KEYS`.

```python
# backend/app/engine/__init__.py
from app.engine.features import (
    FEATURES, FEATURE_KEYS, FeatureSpec, ListingLike, raw_matrix, fit_stats, standardize,
)
from app.engine.mcmc import MCMCConfig, MCMCResult, fit_posterior
from app.engine.diagnostics import Diagnostics
from app.engine.affinity import AffinityResult, Reason, compute_affinity, to_score, explain
from app.engine.pairs import seed_for, random_pairs, next_pair_bald
from app.engine.baselines import Method, fit_mle, predict_proba
from app.engine.evaluation import ResultRow, evaluate_participant, simulate_choices
```

```python
# ---------- features.py ----------
FEATURE_KEYS: tuple[str, ...]          # as 12 chaves da tabela 5.1, nesta ordem
FEATURES: tuple[FeatureSpec, ...]      # mesma ordem

class ListingLike(Protocol):           # serve para a linha do ORM e para ListingRow do catálogo
    price_brl: Decimal | float; area_m2: Decimal | float; bedrooms: int; bathrooms: int
    parking: int; dist_center_km: Decimal | float; age_years: int; kind: str
    leisure_count: int; pet_friendly: bool; doorman_24h: bool

def raw_matrix(rows: Sequence[ListingLike]) -> np.ndarray: ...            # (n, 12) = t(x), antes da padronização
def fit_stats(T: np.ndarray) -> tuple[np.ndarray, np.ndarray]: ...       # (center (12,), scale (12,))
def standardize(T: np.ndarray, center: np.ndarray, scale: np.ndarray) -> np.ndarray: ...  # (n, 12) = z

# ---------- mcmc.py ----------
@dataclass(frozen=True)
class MCMCConfig:
    chains: int = 16; warmup: int = 1000; draws: int = 2000; thin: int = 8; target_accept: float = 0.30

@dataclass(frozen=True)
class MCMCResult:
    samples: np.ndarray        # (S, 12), S = chains * draws // thin = 4000, em ordem por cadeia:
                               # linhas [k*K:(k+1)*K] são a cadeia k, com K = draws // thin
    n_chains: int
    seed: int
    diagnostics: Diagnostics

def fit_posterior(D: np.ndarray, mu: np.ndarray, sd: np.ndarray, seed: int,
                  cfg: MCMCConfig = MCMCConfig()) -> MCMCResult: ...
# D: (m, 12), cada linha = z(vencedor) - z(perdedor). m pode ser 0.
# m = 0: devolve S amostras sorteadas direto de N(mu, sd^2), com diagnostics
#        accept_rate=1.0, rhat_max=1.0, ess_min=S, step_size=0.0, ok=True.
# m > 0: Metropolis-Hastings da seção 5.4, com a regra de nova tentativa da seção 5.5.

# ---------- diagnostics.py ----------
@dataclass(frozen=True)
class Diagnostics:
    accept_rate: float; rhat_max: float; ess_min: float
    step_size: float; elapsed_ms: int; ok: bool   # mesmos nomes do schema Diagnostics da seção 6

# ---------- affinity.py ----------
@dataclass(frozen=True)
class AffinityResult:
    mean: np.ndarray; p5: np.ndarray; p95: np.ndarray   # cada um (n,), valores em [0, 1]

@dataclass(frozen=True)
class Reason:
    feature_key: str; text: str; contribution: float

def compute_affinity(Z: np.ndarray, samples: np.ndarray) -> AffinityResult: ...
# Z (n, 12), samples (S, 12). Para o método "persona": samples = mu[None, :] (S = 1).
def to_score(affinity: float, inspection_delta: int = 0) -> int: ...
# clip(round(100 * affinity) + inspection_delta, 0, 100)
def explain(z: np.ndarray, w_mean: np.ndarray, max_reasons: int = 4) -> list[Reason]: ...
# regra da seção 5.6; z (12,), w_mean (12,)

# ---------- pairs.py ----------
def seed_for(session_id: UUID | str, n: int) -> int: ...
# int.from_bytes(sha256(f"{session_id}:{n}".encode()).digest()[:8], "big")
def random_pairs(n_items: int, n_pairs: int, rng: np.random.Generator,
                 max_appearances: int = 3) -> list[tuple[int, int]]: ...
# índices (esquerda, direita) em 0..n_items-1; sem repetir par; cada índice no máximo
# max_appearances vezes; lado sorteado. ValueError se for impossível.
def next_pair_bald(Z: np.ndarray, samples: np.ndarray, shown: set[frozenset[int]],
                   rng: np.random.Generator, k: int = 300) -> tuple[int, int]: ...
# seção 5.7; devolve (esquerda, direita) em índices de Z; nunca um par de shown.
# Se o corte C3 for aplicado, o serviço usa random_pairs no lugar desta função.

# ---------- baselines.py ----------
Method = Literal["equal", "persona", "mle", "bayes"]
def fit_mle(D: np.ndarray) -> np.ndarray: ...           # (12,), seção 5.8
def predict_proba(method: Method, D: np.ndarray, *, mu: np.ndarray | None = None,
                  samples: np.ndarray | None = None, w_mle: np.ndarray | None = None) -> np.ndarray: ...
# (m,) = probabilidade de o primeiro imóvel de cada linha de D vencer

# ---------- evaluation.py ----------
@dataclass(frozen=True)
class ResultRow:
    participant_code: str; method: Method; n_train: int; split_seed: int
    n_test: int; accuracy: float; log_loss: float

def evaluate_participant(code: str, D: np.ndarray, mu: np.ndarray, sd: np.ndarray, *,
                         n_train_list: tuple[int, ...] = (3, 5, 10, 15), n_splits: int = 20,
                         n_test: int = 10, cfg: MCMCConfig = MCMCConfig()) -> list[ResultRow]: ...
# D (m, 12) = pares do participante, orientados vencedor - perdedor, na ordem respondida; protocolo 5.9
def simulate_choices(D_left_minus_right: np.ndarray, w_true: np.ndarray,
                     rng: np.random.Generator) -> np.ndarray: ...
# (m,) de "A" ou "B", sorteados com P(A) = sigma(w_true . d)
```
