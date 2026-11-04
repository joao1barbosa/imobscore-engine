# E01 · Repositório e instruções dos agentes

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** qua 04/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Criar a estrutura do repositório, as instruções dos agentes, os arquivos de acompanhamento e o Makefile.

## Arquivos permitidos

a estrutura de pastas da seção 3 (pastas vazias com `.gitkeep`); `.gitignore` (Python, Node, `.env`, `.venv/`, `node_modules/`, `dist/`, `__pycache__/`, `.pytest_cache/`); `.editorconfig` (UTF-8, LF, 4 espaços em Python, 2 nos demais); `.env.example` (todas as variáveis da seção 6, com os valores padrão); `Makefile`; `README.md` (só o título e "em construção"); `docs/PLAN.md` (João fornece o conteúdo: exportação deste documento em Markdown); `docs/STATUS.md`; `docs/decisions.md`; `docs/CHECKPOINTS.md`; `docs/mockups/APPROVAL.md`; `AGENTS.md`; `CLAUDE.md`.

## Dependências

nada

## Especificação

- **`AGENTS.md`** (exatamente este conteúdo):

```markdown
# ImobScore — instruções para o executor (papel E)
Antes de qualquer tarefa, leia docs/PLAN.md (seções 1.3, 1.5, 1.7 e a tarefa pedida) e docs/STATUS.md.
- Faça somente a tarefa E indicada no pedido. Uma por vez.
- Edite apenas os arquivos listados no campo "Arquivos" da tarefa.
- Nunca edite: backend/app/engine/, backend/app/seed/, backend/app/analysis/, backend/tests/engine/, docs/mockups/, frontend/src/styles/theme.css, frontend/src/lib/copy.ts, docs/PLAN.md.
- Importe o motor apenas com "from app.engine import ..." (seção 5.10 do plano).
- Textos de tela vêm de frontend/src/lib/copy.ts. Layout e cores vêm do mockup aprovado e de theme.css. Não escreva textos visíveis direto nos componentes.
- Se algo não estiver especificado, não decida: escreva a pergunta em docs/STATUS.md, em "Perguntas abertas", e pare.
- Não adicione dependências nem mude versões. Não apague, pule nem afrouxe testes.
- Termine só com todos os comandos de "Verificação" passando. Registre em docs/STATUS.md e faça um commit "tipo(escopo): ID título".
- Se uma verificação falhar duas vezes seguidas, pare e marque a tarefa como "precisa de revisão do arquiteto".
```
- **`CLAUDE.md`** (exatamente este conteúdo):

```markdown
# ImobScore — instruções para o Claude (papel A, arquiteto)
Antes de qualquer tarefa, leia docs/PLAN.md e docs/STATUS.md.
- Faça só as tarefas A e A-REV da seção 8.2, na ordem.
- Siga o protocolo de checkpoints da seção 1.4: ao terminar cada módulo do motor, explique a João, faça as 3 perguntas, espere cada resposta, tire todas as dúvidas e registre em docs/CHECKPOINTS.md. Só João declara "Entendido: sim". Sem isso, não faça commit do módulo seguinte.
- Siga a seção 1.6 para mockups. Nenhuma tela vai para o executor sem "aprovado" em docs/mockups/APPROVAL.md.
- Mantenha a interface da seção 5.10. Se precisar mudá-la, avise João e atualize docs/PLAN.md na mesma alteração.
- Decisões não previstas: escolha a opção mais simples compatível com o plano e registre em docs/decisions.md.
- Atualize docs/STATUS.md ao fim de cada tarefa.
```
- **`docs/STATUS.md`** começa com os títulos `## Em andamento`, `## Concluídas (ID · data · resumo da verificação)`, `## Correções pendentes (FIX-n)`, `## Perguntas abertas (ID · pergunta · quem responde)` e `## Bloqueios`. `docs/CHECKPOINTS.md` começa com uma seção vazia por checkpoint, de CP1 a CP7. `APPROVAL.md` começa com o cabeçalho `| Tela | Versão | Status | Data | Observações de João |` e uma linha por tela de M1 a M8, com status "pendente".
- **`Makefile`**, com estes alvos e comandos:

```make
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
	cloudflared tunnel --url http://localhost:8080
reset:    ## apaga o banco (pede confirmação)
	@read -p "Apagar o banco? [s/N] " r && [ "$$r" = "s" ] && docker compose down -v
```

## Verificação

`make help` lista os 13 alvos; `git status` limpo depois do commit.
