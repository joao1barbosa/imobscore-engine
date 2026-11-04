# E03 · Esqueleto do back-end

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

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
