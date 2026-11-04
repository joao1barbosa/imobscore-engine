# A07 · Avaliação, simulação e relatório

- **Responsável:** A · Arquiteto (Claude)
- **Prazo:** sex 06/11
- **Fonte:** `docs/PLAN.md`, seção 8.2. Em caso de divergência, vale o plano.

## Objetivo

Implementar o protocolo de avaliação, a simulação de participantes e o relatório com CSV e figuras.

## Arquivos permitidos

`backend/app/engine/evaluation.py`; `backend/app/analysis/__init__.py`; `backend/app/analysis/report.py`; as funções `simulate` e `evaluate` em `backend/app/cli.py`; `backend/tests/engine/test_evaluation.py`.

## Dependências

A06, E09

## Especificação

- **Especificação:** seção 5.9 e o formato JSON da tarefa E09.
- **`simulate --participants 10 --out data/collected/pairs_simulated.json`:** participantes S01 a S10, personas em rodízio (familia, investidor, estudante), segmento de `demo_defaults` da persona, w verdadeiro = μ + N(0; 0,7²), 40 pares de `random_pairs` sobre os candidatos e escolhas por `simulate_choices`. `session_id` fica `null`.
- **`evaluate --from-json <arquivo> --out data/results`:** monta D de cada participante (z = `standardize(t, center, scale)`; vencedor = esquerda se `chosen = "A"`), roda `evaluate_participant` e grava `results.csv` (colunas: `run_id, participant_code, method, n_train, split_seed, n_test, accuracy, log_loss`, com um `run_id` UUID por execução), `summary.csv` (colunas: `method, n_train, acc_mean, acc_sd, ll_mean, ll_sd, n_participants`) e as figuras `accuracy_vs_ntrain.png` e `accuracy_by_participant.png` (seção 5.9). Imprime a tabela resumo no terminal.

## Verificação

`cd backend && uv run pytest tests/engine -q && uv run mypy app/engine` (comando da A02; a tarefa não define um próprio), seguido de `make simulate` e de `docker compose exec api python -m app.cli evaluate --from-json data/collected/pairs_simulated.json --out data/results` (comandos da especificação abaixo).

**Pronto quando:** nos dados simulados, `bayes` e `mle` superam `equal` com n\_train = 25, e Claude mostra as figuras a João.
