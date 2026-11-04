# Imagem da API: Python 3.12 slim com o uv do Astral.
FROM ghcr.io/astral-sh/uv:0.13.6 AS uv

FROM python:3.12-slim

COPY --from=uv /uv /uvx /usr/local/bin/

WORKDIR /app

# Só as dependências primeiro, para a camada do ambiente ficar no cache.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

ENV PATH=/app/.venv/bin:$PATH

COPY . .

CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
