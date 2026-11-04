# E04 · Modelos do banco e migração

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Criar os modelos SQLAlchemy das 8 tabelas e a migração inicial única do Alembic.

## Arquivos permitidos

`backend/app/models/__init__.py`, `base.py`, `listing.py`, `feature_stats.py`, `persona.py`, `session.py`, `comparison.py`, `posterior.py`, `inspection.py`, `experiment_result.py`; `backend/alembic.ini`; `backend/migrations/` (`env.py` e uma única revisão `0001_initial.py`); `backend/tests/test_migrations.py`.

## Dependências

E03

## Especificação

- **Especificação:** o DDL da seção 4, exatamente, com SQLAlchemy 2.0 (`Mapped[...]`). Convenção de nomes no `MetaData`: `ix_%(column_0_label)s`, `uq_%(table_name)s_%(column_0_name)s`, `ck_%(table_name)s_%(constraint_name)s`, `fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s`, `pk_%(table_name)s`. Depois do `--autogenerate`, conferir à mão os `CHECK` e o `gen_random_uuid()`.

## Procedimento obrigatório

Decisão de João (Q4): `backend/migrations/` já existe com um `.gitkeep`, e `alembic init` recusa pasta não vazia. Gere o template em uma pasta temporária e copie sem sobrescrever nada. Rode a partir da raiz do repositório:

```bash
T=$(mktemp -d) && (cd "$T" && uv run --project "$OLDPWD/backend" alembic init migrations)
cp -r --update=none "$T/migrations/." backend/migrations/ && cp --update=none "$T/alembic.ini" backend/ && rm -rf "$T"
```

Por último, apague os `.gitkeep` das pastas que passaram a ter outros arquivos:

```bash
find backend/migrations -path '*/node_modules' -prune -o -name .gitkeep -type f -exec sh -c '[ "$(ls -A "$(dirname "$1")" | wc -l)" -gt 1 ] && rm "$1"; true' _ {} \;
```

## Verificação

um teste roda `upgrade head`, `downgrade base` e `upgrade head` no banco de teste sem erro; `\dt` mostra as 8 tabelas.

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

### Seção 4 · Modelo de dados (PostgreSQL)

São 8 tabelas, criadas por uma única migração inicial do Alembic. O DDL abaixo é a referência: o agente escreve os modelos do SQLAlchemy 2.0 que geram exatamente este esquema e confere com `alembic upgrade head` seguido de `\d+` no `psql`.

| Tabela | Guarda | Escrita por |
| --- | --- | --- |
| `listings` | Os \~300 imóveis simulados e seus atributos brutos | Comando `seed` |
| `feature_stats` | Centro (mediana) e escala de cada característica, por cidade e finalidade | Comando `seed` |
| `personas` | Família, Investidor e Estudante, com média e desvio da priori | Comando `seed` (de `personas.yaml`) |
| `sessions` | Uma pessoa: respostas do onboarding, persona e modo | `POST /sessions` |
| `comparisons` | Cada par mostrado e a escolha feita | Fluxo de comparações |
| `posteriors` | Amostras do MCMC e resumo, por sessão e por número de pares | Serviço do motor |
| `inspections` | Ajustes da vistoria (Δ de −10 a +10) por sessão e imóvel | Tela de detalhe |
| `experiment_results` | Métricas de cada método por participante e tamanho de treino | Comando `evaluate` |

```sql
CREATE TABLE listings (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code            text UNIQUE NOT NULL,              -- ex.: GYN-V-0042
  city            text NOT NULL,                     -- só 'Goiânia' no MVP
  purpose         text NOT NULL CHECK (purpose IN ('sale','rent')),
  kind            text NOT NULL CHECK (kind IN ('apartment','house')),
  title           text NOT NULL,
  neighborhood    text NOT NULL,
  price_brl       numeric(12,2) NOT NULL CHECK (price_brl > 0), -- só venda no MVP
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

CREATE TABLE inspections (
  session_id  uuid NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  listing_id  uuid NOT NULL REFERENCES listings(id),
  item_key    text NOT NULL,                         -- chave de inspection_items.yaml
  delta       smallint NOT NULL CHECK (delta BETWEEN -10 AND 10),
  created_at  timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (session_id, listing_id, item_key)
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

**Regras do banco**

- As características transformadas e padronizadas não são guardadas. Elas são recalculadas em memória a partir de `listings` e `feature_stats`, porque são baratas e assim a fórmula fica em um só lugar (`engine/features.py`).
- `posteriors.samples` guarda as amostras em `float32` (cerca de 4.000 × 12 × 4 bytes = 192 kB por linha). O feed reaproveita a última posteriori em vez de rodar o MCMC de novo.
- `comparisons.chosen` fica nulo entre mostrar o par e receber a resposta, o que permite retomar a sessão após recarregar a página.
- A convenção de nomes do SQLAlchemy (`ix_`, `uq_`, `ck_`, `fk_`, `pk_`) é definida no `MetaData` antes da primeira migração.
