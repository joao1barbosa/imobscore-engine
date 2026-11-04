# E09 · Docker completo, exportação e túnel

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qui 05/11, até 17h
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Completar o Docker Compose, o comando export e o túnel, deixando a coleta acessível aos colegas.

## Arquivos permitidos

`backend/Dockerfile`; `frontend/Dockerfile`; `frontend/nginx.conf`; `docker-compose.yml` (serviços `api` e `web` da seção 10); o comando `export` em `backend/app/cli.py`; `backend/app/services/export_service.py`; `backend/tests/services/test_export.py`; `README.md` (como rodar e o túnel).

## Dependências

E07, E08

## Especificação

- **`backend/Dockerfile`:** `python:3.12-slim`; copiar o `uv` da imagem `ghcr.io/astral-sh/uv`; `WORKDIR /app`; `uv sync --frozen --no-dev`; `ENV PATH=/app/.venv/bin:$PATH`; `CMD sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"`.
- **`frontend/Dockerfile`:** estágio de build com `node:24-alpine` e `corepack enable`, `pnpm install --frozen-lockfile`, `pnpm build`; estágio final `nginx:alpine` com o `dist/` em `/usr/share/nginx/html`.
- **`nginx.conf`:** `location /api/ { proxy_pass http://api:8000; }` e `location / { try_files $uri /index.html; }`.
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
- **Regras do export:** só sessões `collection` com pelo menos 35 pares respondidos; se um código tiver mais de uma sessão, fica a de mais pares respondidos (empate: a mais recente); só pares respondidos, em ordem de `position`; `t_left` e `t_right` são as linhas de `raw_matrix` (antes da padronização); `center` e `scale` vêm de `feature_stats` do segmento.

## Verificação

`make up` a partir de um clone limpo, seguido de `make seed`, sobe tudo; `curl http://localhost:8080/api/v1/health` responde ok; `make tunnel` gera um endereço, e um celular fora da rede local completa os 40 pares por ele; `make export` gera um JSON válido com esse participante. **João envia o link aos colegas às 18h**, com o código de cada um (P01 a P10).
