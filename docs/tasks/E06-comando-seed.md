# E06 · Comando seed

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11, noite
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Implementar o comando seed, que popula catálogo, personas e estatísticas de padronização.

## Arquivos permitidos

`backend/app/cli.py` (app Typer, rodado com `python -m app.cli`; deixar as funções `simulate` e `evaluate` para a A07); `o arquivo termina com if __name__ == "__main__": app()`; `backend/app/services/__init__.py`; `backend/app/services/seed_service.py`; `backend/tests/services/test_seed.py`.

## Dependências

A02, E04

## Especificação

- **`seed [--force] [--if-empty] [--with-results]`:**
  1. Se existir alguma linha em `sessions` e não houver `--force`, parar com a mensagem "Existem sessões; use --force para apagar tudo".
  2. Com `--if-empty` e `listings` não vazia, não fazer nada além do passo 6.
  3. Em uma transação: `TRUNCATE` de todas as tabelas, com `CASCADE`.
  4. Inserir `generate_catalog(settings.CATALOG_SEED)` em `listings` e as personas de `app/seed/personas.yaml` em `personas`.
  5. Para cada (cidade, finalidade): `T = raw_matrix(listings do segmento)`, `center, scale = fit_stats(T)` e uma linha em `feature_stats` por chave de `FEATURE_KEYS`.
  6. Com `--with-results` e `data/results/results.csv` existente: carregar esse CSV como em `load-results` (E10).

## Verificação

`pytest tests/services/test_seed.py` confere 300 imóveis, 3 personas e 72 linhas de `feature_stats`; rodar duas vezes gera os mesmos códigos e preços.

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

CREATE TABLE experiment_results (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  run_id           uuid NOT NULL,
  participant_code text NOT NULL,
  method           text NOT NULL CHECK (method IN ('equal','persona','mle','bayes')),
  n_train          smallint NOT NULL,                -- 3, 5, 10, 15, 25
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
```

### Tarefa A02 · O que o arquiteto entrega

- **Catálogo:** `generate_catalog(seed: int) -> list[ListingRow]`, em que `ListingRow` é uma dataclass imutável com os campos da tabela `listings` (seção 4), exceto `id` e `created_at`. São 300 imóveis: 3 cidades × 2 finalidades × 50. Tudo vem de `rng = np.random.default_rng(seed)`, nesta ordem fixa de geração: cidade, finalidade, índice.
- **`personas.yaml`:** lista com `slug`, `name`, `description` (1 frase), `prior_mean` (as 12 chaves da tabela 5.3), `prior_sd` (12 chaves, todas 1,0) e `demo_defaults` (`city`, `purpose`, `price_min`, `price_max`, com os valores da seção 5.3).

### Tarefa E10 · `load-results`

- **`load-results <csv>`:** insere as linhas em `experiment_results`; se o `run_id` já existir, não faz nada e avisa.
