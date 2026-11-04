# E09 · Docker completo, exportação e túnel

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qui 05/11, até 17h
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Completar o Docker Compose, o comando export e o túnel, deixando a coleta acessível aos colegas.

## Arquivos permitidos

`backend/Dockerfile`; `frontend/Dockerfile`; `frontend/nginx.conf`; `docker-compose.yml` (serviços `api` e `web` da seção 10); o comando `export` em `backend/app/cli.py`; `backend/app/services/export_service.py`; `backend/tests/services/test_export.py`; `README.md` (como rodar e o túnel).

## Dependências

E07, E08

## Especificação

- **`backend/Dockerfile`:** `python:3.12-slim`; copiar o `uv` da imagem `ghcr.io/astral-sh/uv`; `WORKDIR /app`; `uv sync --frozen --no-dev`; `ENV PATH=/app/.venv/bin:$PATH`; `CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"`.
- **`frontend/Dockerfile`:** estágio de build com `node:24-alpine` e `corepack enable`, `pnpm install --frozen-lockfile`, `pnpm build`; estágio final `nginx:alpine` com o `dist/` em `/usr/share/nginx/html`.
- **`nginx.conf`:** `location /api/ { proxy_pass http://api:8000; }` e `location / { try_files $uri /index.html; }`. No bloco `server`, `access_log off;`, para o servidor não registrar o IP de quem responde à coleta, porque a tela inicial promete que nenhum dado pessoal é coletado.
- **`export --out <arquivo>`:** grava JSON neste formato exato (lido pela A07):

```json
{
  "exported_at": "2026-11-08T12:05:00-03:00",
  "feature_keys": ["log_price", "log_area", "...as 12 chaves"],
  "participants": [
    {
      "participant_code": "P01",
      "session_id": "uuid ou null",
      "persona_slug": "familia",
      "city": "Goiânia",
      "purpose": "sale",
      "center": [12 números],
      "scale": [12 números],
      "pairs": [
        {"position": 1, "left_code": "GYN-V-0012", "right_code": "GYN-V-0031",
         "t_left": [12 números], "t_right": [12 números], "chosen": "A", "response_ms": 2310}
      ]
    }
  ]
}
```
- **Regras do export:** só sessões `collection` com pelo menos 25 pares respondidos; cada sessão tem o próprio código; só pares respondidos, em ordem de `position`; `t_left` e `t_right` são as linhas de `raw_matrix` (antes da padronização); `center` e `scale` vêm de `feature_stats` do segmento.

## Verificação

`make up` a partir de um clone limpo, seguido de `make seed`, sobe tudo; `curl http://localhost:8080/api/v1/health` responde ok; `make tunnel` gera um endereço, e um celular fora da rede local completa os 25 pares por ele; `make export` gera um JSON válido com esse participante. **João envia o link aos colegas às 18h**; o mesmo link serve para todos.

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

### Seção 10 · Docker Compose, seed e demo offline

No dia, o notebook roda `make demo` sem internet e abre o navegador em `http://localhost:8080/demo`. Todas as imagens e dependências são baixadas antes, em casa.

```yaml
# docker-compose.yml (referência exata)
services:
  db:
    image: postgres:17-alpine
    environment:
      POSTGRES_USER: imobscore
      POSTGRES_PASSWORD: imobscore
      POSTGRES_DB: imobscore
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./docker/initdb:/docker-entrypoint-initdb.d:ro
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U imobscore"]
      interval: 3s
      retries: 20
    ports: ["5432:5432"]          # usado por make dev e pelos testes
  api:
    build: ./backend
    env_file: .env
    environment:
      DATABASE_URL: postgresql+psycopg://imobscore:imobscore@db:5432/imobscore
    volumes:
      - ./data:/app/data            # pares exportados e resultados ficam no repositório
    depends_on:
      db: { condition: service_healthy }
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"]
      interval: 5s
      retries: 20
  web:
    build: ./frontend
    ports: ["8080:80"]
    depends_on:
      api: { condition: service_healthy }
volumes:
  pgdata:
```

O serviço `db` publica a porta 5432 para `make dev` e para os testes. O `.env` local usa `DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore` e `TEST_DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore_test`. Os comandos `make` estão definidos na tarefa E01.

**Checklist da véspera (10/11)**

- [ ] Com internet: `docker compose pull` e `make up`, para deixar todas as imagens no cache do notebook.
- [ ] Desligar o Wi-Fi e repetir o roteiro manual da seção 9 a partir de `make reset` e `make demo`.
- [ ] Conferir que `data/collected/pairs.json` e `data/results/` estão no repositório. O `make demo` recarrega os resultados a partir deles, mesmo com o banco recriado.
- [ ] Desativar a suspensão de tela e as atualizações automáticas do sistema.
- [ ] Deixar um segundo navegador aberto no painel do experimento, ao lado da demo.
- [ ] Plano B: gravar um vídeo de 60 segundos da demo.
- [ ] Ler `docs/demo-script.md` em voz alta uma vez.

### Seção 4 · Tabelas usadas pelo export

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
```

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

### Seção 12 · Acesso dos colegas à coleta

| Como os colegas acessam a coleta? | Túnel do Cloudflare com o notebook ligado de 05/11, 18h, a 08/11, 12h | Coleta presencial no notebook; deploy mínimo só da coleta | qui 05/11, 12h |
