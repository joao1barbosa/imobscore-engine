# E03 · Esqueleto do back-end

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** este arquivo é autocontido e é o que vale. Consulte `docs/PLAN.md` (seção 8.3) só se faltar algo aqui, lendo apenas a seção necessária.

## Objetivo

Criar o esqueleto do back-end: dependências, configuração, erros, rota de saúde e fixtures de teste.

## Arquivos permitidos

`backend/pyproject.toml`; `backend/uv.lock`; `backend/app/__init__.py`; `backend/app/main.py`; `backend/app/config.py`; `backend/app/db.py`; `backend/app/deps.py`; `backend/app/errors.py`; `backend/app/api/__init__.py`; `backend/app/api/v1/__init__.py`; `backend/app/api/v1/health.py`; `backend/tests/conftest.py`; `backend/tests/api/test_health.py`.

## Dependências

E02

## Especificação

- **Dependências** (`uv add`): `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `sqlalchemy`, `psycopg[binary]`, `alembic`, `numpy`, `scikit-learn`, `matplotlib`, `typer`, `pyyaml`. Desenvolvimento (`uv add --dev`): `pytest`, `pytest-cov`, `httpx`, `ruff`, `mypy`, `scipy`. Python 3.12. Nada além disso.
- **`config.py`:** classe `Settings(BaseSettings)` com os campos e padrões da lista "Configuração" da seção 6, mais `TEST_DATABASE_URL`. `get_settings()` com `lru_cache`.
- **`main.py`:** cria `FastAPI(title="ImobScore")`, registra o handler de erros de `errors.py` (formato da seção 6), o CORS com `CORS_ORIGINS` e o router `/api/v1`.
- **`errors.py`:** `class ApiError(Exception)` com `status`, `code` e `message`, e os handlers de `ApiError` e `RequestValidationError` (este devolve `422 validation_error`).
- **`conftest.py`:** fixture `db` que conecta em `TEST_DATABASE_URL`, abre uma transação por teste e faz rollback no fim; fixture `client` com `TestClient` e `get_db` sobrescrito.
- **`pyproject.toml`:** Ruff com `line-length = 100` e regras `E, F, I, B, UP`; mypy `strict = true` só para `app.engine.*`; pytest com o marcador `perf` registrado.

## Verificação

`cd backend && uv run pytest -q && uv run ruff check . && uv run ruff format --check .`; `GET /api/v1/health` devolve `{"status": "ok", "db": "ok"}`.

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

### Seção 2 · Stack do back-end

| Ferramenta | Versão | Para quê |
| --- | --- | --- |
| Python | 3.12 | Linguagem do back-end e do motor |
| uv | atual | Gerenciador de pacotes e ambientes, com lockfile reprodutível |
| FastAPI | atual | API HTTP com OpenAPI gerado automaticamente |
| Uvicorn | atual | Servidor ASGI |
| Pydantic v2 + pydantic-settings | 2.x | Schemas da API e configuração por variáveis de ambiente |
| SQLAlchemy | 2.0 | ORM no estilo 2.0 (`Mapped[...]`), com sessões síncronas |
| psycopg | 3.x | Driver do PostgreSQL |
| Alembic | 1.x | Migrações do banco |
| PostgreSQL | 17 | Banco de dados, via imagem `postgres:17-alpine` |
| NumPy | 2.x | Motor: verossimilhança, Metropolis-Hastings e afinidade |
| scikit-learn | 1.x | Só o baseline de máxima verossimilhança (`LogisticRegression`) |
| SciPy | 1.x | Só nos testes (otimizador para conferir o MAP) |
| Faker (pt\_BR) | atual | \[não usar\] O catálogo usa listas fixas de bairros (tarefa A02), para ser determinístico entre versões |
| Matplotlib | 3.x | Figuras do relatório, geradas pelo script de avaliação |
| Typer | atual | Comandos de linha (`seed`, `evaluate`, `export`) |
| pytest + pytest-cov + httpx | atual | Testes unitários e de API |
| Ruff | atual | Lint e formatação |
| mypy (modo `strict` em `app/engine`) | atual | Checagem de tipos |

O banco usa sessões síncronas, porque o motor é CPU puro e o MVP tem poucos usuários. Async não traria ganho e complicaria os testes. As rotas que rodam o MCMC são `def`, e não `async def`, para o FastAPI rodá-las no pool de threads.

### Seção 3 · Camadas do back-end

- `api/` (rotas): valida a entrada com Pydantic, chama um serviço e devolve um schema. Não contém regra de negócio.
- `services/`: busca dados no banco, monta as matrizes, chama o motor e grava o resultado. Toda transação abre e fecha aqui.
- `engine/`: só matemática. Nenhum import de SQLAlchemy, FastAPI ou Pydantic. O mypy roda em modo `strict` nesta pasta.
- `models/`: tabelas do SQLAlchemy. `schemas/`: modelos Pydantic de entrada e saída.

### Seção 3 · Estrutura do back-end

```text
├── backend/
│   ├── pyproject.toml
│   ├── uv.lock
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── migrations/
│   ├── app/
│   │   ├── main.py           # cria o FastAPI, CORS, routers
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── db.py             # engine e SessionLocal
│   │   ├── deps.py           # get_db, get_session_or_404
│   │   ├── api/v1/           # meta.py sessions.py feed.py listings.py experiment.py
│   │   ├── models/           # listing.py persona.py session.py comparison.py ...
│   │   ├── schemas/
│   │   ├── services/         # session_service.py pair_service.py feed_service.py ...
│   │   ├── analysis/
│   │   │   └── report.py     # summary.csv e figuras do experimento (A07)
│   │   ├── engine/
│   │   │   ├── __init__.py   # interface pública do motor (seção 5.10)
│   │   │   ├── features.py   # especificação e transformação das 12 características
│   │   │   ├── model.py      # sigmoide, log-verossimilhança, log-priori, log-posteriori
│   │   │   ├── mcmc.py       # Metropolis-Hastings vetorizado
│   │   │   ├── diagnostics.py# R-hat, ESS, taxa de aceitação
│   │   │   ├── affinity.py   # afinidade, intervalo e explicação
│   │   │   ├── pairs.py      # escolha do próximo par
│   │   │   ├── baselines.py  # pesos iguais, persona, máxima verossimilhança
│   │   │   └── evaluation.py # protocolo de avaliação e simulação (5.9)
│   │   ├── seed/
│   │   │   ├── personas.yaml
│   │   │   ├── inspection_items.yaml
│   │   │   └── catalog.py    # gerador do catálogo simulado
│   │   └── cli.py            # Typer: seed, evaluate, export, simulate
│   └── tests/
│       ├── engine/
│       ├── services/
│       └── api/
```

### Seção 6 · Erros, CORS e configuração

- **Erros:** formato único `{"detail": {"code": "...", "message": "..."}}`, com mensagem em pt-BR. Códigos: `session_not_found` (404), `listing_not_found` (404), `pair_already_answered` (409), `pair_out_of_order` (409), `session_done` (409), `validation_error` (422), `not_available` (501). Um handler global converte o `RequestValidationError` do FastAPI para esse formato.
- **CORS:** liberado só para `http://localhost:5173` (desenvolvimento). Com o Docker Compose, o Nginx serve front-end e API na mesma origem.
- **Configuração (`.env`):** `DATABASE_URL`, `MCMC_CHAINS=16`, `MCMC_WARMUP=1000`, `MCMC_DRAWS=2000`, `MCMC_THIN=8`, `PRIOR_SD=1.0`, `PAIRS_DEMO=3`, `PAIRS_PRODUCT=8`, `PAIRS_COLLECTION=40`, `CATALOG_SEED=42`, `LOG_LEVEL=INFO`, `CORS_ORIGINS=http://localhost:5173`.

### Seção 10 · Variáveis do `.env` local

O serviço `db` publica a porta 5432 para `make dev` e para os testes. O `.env` local usa `DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore` e `TEST_DATABASE_URL=postgresql+psycopg://imobscore:imobscore@localhost:5432/imobscore_test`. Os comandos `make` estão definidos na tarefa E01.
