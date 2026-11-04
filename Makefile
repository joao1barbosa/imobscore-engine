API = docker compose exec api python -m app.cli
.PHONY: help up down dev seed demo check test export simulate evaluate tunnel reset
help:     ## lista os alvos
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/ -/'
up:       ## sobe db, api e web
	docker compose up -d --build
down:     ## para tudo
	docker compose down
dev:      ## sobe só o banco e mostra como rodar API e front localmente
	docker compose up -d db
	@echo "Terminal 1: cd backend && uv run uvicorn app.main:app --reload --port 8000"
	@echo "Terminal 2: cd frontend && pnpm dev"
seed:     ## recria catálogo, personas e estatísticas
	$(API) seed --force
demo:     ## sobe tudo, semeia se vazio e abre o modo demo
	docker compose up -d --build
	$(API) seed --if-empty --with-results
	@xdg-open http://localhost:8080/demo 2>/dev/null || open http://localhost:8080/demo
check:    ## lint, tipos e testes do back-end e do front-end
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app/engine && uv run pytest -q -m "not perf"
	cd frontend && pnpm lint && pnpm format:check && pnpm typecheck && pnpm test:run
test:     ## só os testes
	cd backend && uv run pytest -q
	cd frontend && pnpm test:run
export:   ## grava os pares da coleta em data/collected/pairs.json
	$(API) export --out data/collected/pairs.json
simulate: ## gera participantes simulados
	$(API) simulate --participants 10 --out data/collected/pairs_simulated.json
evaluate: ## exporta, avalia e carrega os resultados no banco
	$(API) export --out data/collected/pairs.json
	$(API) evaluate --from-json data/collected/pairs.json --out data/results
	$(API) load-results data/results/results.csv
tunnel:   ## expõe a porta 8080 para a coleta
	cloudflared tunnel --url http://localhost:8080 --protocol http2
reset:    ## apaga o banco (pede confirmação)
	@read -p "Apagar o banco? [s/N] " r && [ "$$r" = "s" ] && docker compose down -v
