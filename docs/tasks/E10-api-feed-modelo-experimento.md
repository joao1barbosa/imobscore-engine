# E10 · API do feed, do modelo e do experimento

- **Responsável:** E · Executor (OpenCode Go)
- **Prazo:** sex 06/11
- **Fonte:** `docs/PLAN.md`, seção 8.3. Em caso de divergência, vale o plano.

## Objetivo

Implementar as rotas e os serviços de posteriori, feed, modelo e experimento, além do modo adaptativo de pares.

## Arquivos permitidos

`backend/app/services/posterior_service.py`, `feed_service.py`, `experiment_service.py`, `pair_service.py` (acrescentar o modo adaptativo); `backend/app/schemas/feed.py`, `posterior.py`, `experiment.py`; `backend/app/api/v1/feed.py`, `posterior.py`, `experiment.py`, `meta.py` (acrescentar `/meta/features` e `/meta/inspection-items`), `sessions.py` (acrescentar o recálculo depois da resposta); o comando `load-results` em `backend/app/cli.py`; testes em `backend/tests/api/` e `backend/tests/services/`.

## Dependências

A06 concluída em `docs/STATUS.md`

## Especificação

- **`posterior_service.get_or_fit(session, n) -> MCMCResult`:** se existir linha em `posteriors` com `(session_id, n_comparisons = n)`, carrega as amostras (`np.load` do `bytea`, convertido para `float64`) e devolve. Senão: D = z(vencedor) − z(perdedor) dos n primeiros pares respondidos, em ordem de `position`, com z = `standardize(raw_matrix(...), center, scale)` do segmento da sessão; `mu` e `sd` vêm de `personas.prior_mean` e `prior_sd`, na ordem de `FEATURE_KEYS`; `fit_posterior(D, mu, sd, seed_for(session.id, n), MCMCConfig(...))` com os valores de `MCMC_*` das configurações; grava a linha (amostras em `float32` com `np.save`, `mean`, `sd`, `ci_low` e `ci_high` por chave, campos de diagnóstico e `seed`) e devolve.
- **Depois de cada resposta** (`POST /comparisons`), nos modos `demo` e `product`: chamar `get_or_fit(session, answered)` e devolver os diagnósticos em `AnswerOut`. No modo `collection`, não roda MCMC e devolve `diagnostics = null`.
- **`GET /next-pair` nos modos `demo` e `product`:** candidatos de `candidate_listings`; `Z` padronizado; `samples = get_or_fit(session, answered).samples`; `shown` = conjunto de `frozenset({i, j})` dos pares já mostrados, em índices dos candidatos; `next_pair_bald(Z, samples, shown, np.random.default_rng(seed_for(session.id, 10_000 + answered)))`; gravar com `selection = 'adaptive'`. Com o corte C3, usar `random_pairs` como na coleta.
- **`GET /sessions/{id}/feed?method=bayes|persona&at=N&limit=30&offset=0`:** `n = at` se informado, senão `answered`; `at` fora de 0..answered devolve 422. `bayes`: `samples` de `get_or_fit(session, n)`, `compute_affinity(Z, samples)` e `explain(Z[i], samples.mean(0))`. `persona`: `samples = mu[None, :]` e `reasons = []`. Cada `FeedItem`: `score = to_score(mean[i], 0)`, `affinity_pct = round(100 * mean[i], 1)`, `interval = (round(100 * p5[i], 1), round(100 * p95[i], 1))`, `inspection_delta = 0`, `rank` a partir de 1. Ordem e cache conforme a seção 6.
- **`GET /sessions/{id}/posterior?n=`:** um `WeightOut` por chave, com `label` de `FEATURES`, priori da persona e média, desvio e percentis 5 e 95 das amostras; mais os diagnósticos. `n` padrão: `answered`.
- **`GET /sessions/{id}/posterior/trace?feature=<chave>&n=`:** `TraceOut = { feature_key: str, chains: list[list[float]] }`, com `samples.reshape(n_chains, -1, 12)[:4, :, j]`. Chave fora de `FEATURE_KEYS` devolve 422.
- **`GET /experiment/summary?run_id=`:** sem `run_id`, usa a rodada mais recente (maior `created_at`). Schemas:

```python
class ExperimentRow(BaseModel):
    method: Literal["equal", "persona", "mle", "bayes"]; n_train: int
    acc_mean: float; acc_sd: float; ll_mean: float; ll_sd: float; n_participants: int
class ParticipantRow(BaseModel):
    participant_code: str; method: str; acc_mean: float      # sempre n_train = 5
class ExperimentSummary(BaseModel):
    run_id: UUID | None; simulated: bool; participants: int
    rows: list[ExperimentRow]; per_participant: list[ParticipantRow]
```

`simulated` é verdadeiro se algum `participant_code` começar com "S". Sem resultados: `run_id = null` e listas vazias.
- **`load-results <csv>`:** insere as linhas em `experiment_results`; se o `run_id` já existir, não faz nada e avisa.
- **Testes:** feed com 0 e com 3 pares; `method=persona`; `at=0` diferente de `at=3`; `at` inválido dá 422; score sempre entre 0 e 100; segunda chamada do feed não roda o MCMC de novo (verificar com `unittest.mock`); posteriori com 12 pesos; traço com 4 cadeias de 250 pontos; resumo vazio e com um CSV de exemplo; demo com 3 pares sem repetir.

## Verificação

`cd backend && uv run pytest -q && uv run ruff check .`.
