# E07 · API da coleta

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qui 05/11, manhã
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Implementar as rotas de metadados, sessões e pares aleatórios usadas pela coleta.

## Arquivos permitidos

`backend/app/schemas/__init__.py`, `meta.py`, `session.py`, `listing.py`, `pair.py`; `backend/app/services/listing_service.py` (`candidate_listings`), `session_service.py`, `pair_service.py`; `backend/app/api/v1/meta.py`, `sessions.py`; `backend/tests/api/test_meta.py`, `test_sessions.py`, `test_pairs_collection.py`.

## Dependências

A03, E06

## Especificação

- **Rotas:** `GET /meta/options`, `GET /meta/personas`, `POST /sessions`, `GET /sessions/{id}`, `GET /sessions/{id}/next-pair`, `POST /sessions/{id}/comparisons/{position}`, com os schemas e as regras da seção 6.
- **`MetaOptions`:** `{ segments: [{ city, purpose, price_floor, price_ceiling }] }`, com o menor e o maior preço de cada segmento.
- **`POST /sessions`:** `target_pairs` vem de `PAIRS_DEMO`, `PAIRS_PRODUCT` ou `PAIRS_COLLECTION`, conforme `mode`. Na coleta, exige `participant_code` e `consent = true`, e grava `consent_at = now()`. O mesmo código pode abrir mais de uma sessão (o colega pode trocar de aparelho).
- **Pares da coleta:** os candidatos são `candidate_listings(session)` (seção 6), ordenados por `code`. A lista dos 40 pares é `random_pairs(len(candidatos), target_pairs, np.random.default_rng(seed_for(session.id, 0)))`, recalculada de forma determinística a cada chamada. O par da posição k é o k-ésimo da lista, gravado em `comparisons` com `selection = 'random'` na primeira vez que for pedido.
- **Modos `demo` e `product`:** `POST /sessions` já funciona, mas `GET /next-pair` devolve `501 not_available` até a E10.
- **Testes:** criação com e sem consentimento; 40 pares sem repetir; recarregar devolve o mesmo par pendente; 409 em resposta repetida e fora de ordem; 204 depois do 40º par e `status = done`; 404 com sessão inexistente; 422 com `price_min >= price_max`.

## Verificação

`cd backend && uv run pytest -q tests/api`.

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
    participant_code: str | None = Field(default=None, pattern=r"^P\d{2}$")
    consent: bool = False
    # model_validator: price_min < price_max; collection exige participant_code e consent=True

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
- **Configuração (`.env`):** `DATABASE_URL`, `MCMC_CHAINS=16`, `MCMC_WARMUP=1000`, `MCMC_DRAWS=2000`, `MCMC_THIN=8`, `PRIOR_SD=1.0`, `PAIRS_DEMO=3`, `PAIRS_PRODUCT=8`, `PAIRS_COLLECTION=40`, `CATALOG_SEED=42`, `LOG_LEVEL=INFO`, `CORS_ORIGINS=http://localhost:5173`.

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
  target_pairs     smallint NOT NULL,                 -- demo 3, produto 8, coleta 40
  participant_code text,                             -- só na coleta: P01..P10
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
```

### Seção 4 · Regras do banco

- As características transformadas e padronizadas não são guardadas. Elas são recalculadas em memória a partir de `listings` e `feature_stats`, porque são baratas e assim a fórmula fica em um só lugar (`engine/features.py`).
- `posteriors.samples` guarda as amostras em `float32` (cerca de 4.000 × 12 × 4 bytes = 192 kB por linha). O feed reaproveita a última posteriori em vez de rodar o MCMC de novo.
- `comparisons.chosen` fica nulo entre mostrar o par e receber a resposta, o que permite retomar a sessão após recarregar a página.
- A convenção de nomes do SQLAlchemy (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) é definida no `MetaData` antes da primeira migração.

### Seção 5.7 · Escolha do próximo par

- **Candidatos:** imóveis do segmento da sessão com preço entre 0,85 × `price_min` e 1,15 × `price_max`. Se forem menos de 20, use o segmento inteiro.
- **Modo `collection` (coleta):** pares sorteados ao acaso (`selection = 'random'`), sem repetir par e com cada imóvel aparecendo no máximo 3 vezes. A coleta não roda MCMC entre os pares. Os pares precisam ser aleatórios para que a avaliação não dependa de nenhum dos modelos comparados.
- **Modos `product` e `demo`:** escolha adaptativa (`selection = 'adaptive'`). Sorteie K = 300 pares candidatos ainda não mostrados e escolha o de maior informação esperada (BALD). Antes do primeiro par, use 4.000 amostras sorteadas direto da priori.

```latex
p_s = \sigma\left(w_s^\top (z_A - z_B)\right), \quad \bar p = \frac{1}{S}\sum_s p_s, \quad H(p) = -p\log p - (1-p)\log(1-p), \quad \text{BALD} = H(\bar p) - \frac{1}{S}\sum_s H(p_s)
```

- Sorteie qual imóvel vai à esquerda, para não haver viés de posição. O da esquerda é sempre `listing_a`.
- No modo demo, o MCMC roda depois de cada resposta, porque o próximo par depende da posteriori atual.

### Seção 5.10 · Interface do motor usada

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
```
